window.VisionAI = {
    stream: null,
    isAutoMode: false,
    autoInterval: null,
    videoEl: null,
    canvasEl: null,
    logEl: null,

    init: function () {
        this.videoEl = document.getElementById('camera-feed');
        this.canvasEl = document.getElementById('camera-canvas');
        this.logEl = document.getElementById('vision-log');

        console.log("VISION: Başlatılıyor...");
        // this.startCamera();

        // Auto-Scan Default On
        setTimeout(() => {
            // if (!this.autoInterval) this.toggleAutoScan();
        }, 2000);
    },

    startCamera: async function () {
        try {
            if (this.stream) return;

            // Force constraint
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "user" },
                audio: false
            });
            this.videoEl.srcObject = this.stream;

            // Explicit Play (Chrome Policy)
            try { await this.videoEl.play(); } catch (e) { console.warn("Autoplay blocked, user must interact"); }

            this.log("Kamera bağlantısı kuruldu.", "info");
        } catch (err) {
            console.error(err);
            this.log("HATA: Kamera açılamadı!", "error");
            Swal.fire({ icon: 'error', title: 'Kamera Hatası', text: 'Kamera izni verilmedi veya cihaz bulunamadı.' });
        }
    },

    stopCamera: function () {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
    },

    captureFrame: function () {
        if (!this.stream) return null;

        const context = this.canvasEl.getContext('2d');
        this.canvasEl.width = this.videoEl.videoWidth;
        this.canvasEl.height = this.videoEl.videoHeight;
        context.drawImage(this.videoEl, 0, 0, this.canvasEl.width, this.canvasEl.height);

        return this.canvasEl.toDataURL('image/jpeg', 0.8); // Compress quality
    },

    analyzeNow: async function (isAuto = false) {
        const frame = this.captureFrame();
        if (!frame) {
            this.log("Görüntü alınamadı!", "error");
            return;
        }

        if (!isAuto) {
            this.log("Görüntü analiz ediliyor...", "info");
            // Görsel efekt
            this.videoEl.style.filter = "grayscale(100%) contrast(1.2)";
            setTimeout(() => this.videoEl.style.filter = "none", 200);
        }

        try {
            // URL kök dizine alındı (/api yok)
            const res = await fetch('/vision_scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: frame, prompt: isAuto ? "Kısaca ne görüyorsun?" : "Ne görüyorsun? Detaylı anlat." })
            });

            const data = await res.json();

            if (data.success && data.analysis) {
                this.log(data.analysis, "ai");

                // WATCHDOG TRIGGER (Eğer fonksiyon tanımlıysa)
                if (window.checkWatchdogTriggers) {
                    window.checkWatchdogTriggers(data);
                }
            } else {
                // Hata mesajını göster
                const errMsg = data.analysis || data.detail || data.error || "Bilinmeyen hata.";
                this.log("Analiz Başarısız: " + errMsg, "error");
            }
        } catch (err) {
            console.error(err);
            // Hata detayını göster (Serverdan gelen detail)
            let msg = "Analiz başarısız oldu.";
            if (err.detail) msg += "\n" + err.detail;
            else if (err.message) msg += "\n" + err.message;

            Swal.fire({
                icon: 'error',
                title: 'GÖRÜŞ SİSTEMİ HATASI',
                text: msg,
                background: '#0f172a',
                color: '#fff'
            });
            this.log("Görüş sistemi hatası.", "error");
        }
    },

    toggleAutoScan: function (forceOn = false) {
        if (!forceOn) this.isAutoMode = !this.isAutoMode;
        else this.isAutoMode = true;

        const btn = document.getElementById('btn-cam-auto');
        const disp = document.getElementById('cam-mode-disp');
        const status = document.getElementById('vision-status');

        if (this.isAutoMode) {
            if (btn) {
                btn.innerHTML = '<i class="fa-solid fa-stop"></i> OTO DURDUR';
                btn.classList.add('animate-pulse');
            }
            if (disp) {
                disp.innerText = "AUTO-SCAN";
                disp.className = "text-green-400 font-bold";
            }
            if (status) status.innerText = "MONITORING";

            this.log("GİZLİ BEKÇİ MODU: AKTİF", "warning");

            // İlkini hemen yap
            this.analyzeNow(true);

            if (this.autoInterval) clearInterval(this.autoInterval);
            this.autoInterval = setInterval(() => {
                this.analyzeNow(true);
            }, 60000); // 60 saniyede bir

        } else {
            if (btn) {
                btn.innerHTML = '<i class="fa-solid fa-robot"></i> OTO İZLE';
                btn.classList.remove('animate-pulse');
            }
            if (status) status.innerText = "PAUSED";

            clearInterval(this.autoInterval);
            this.log("Bekçi modu duraklatıldı.", "info");
        }
    },

    toggleAuto: function () { this.toggleAutoScan(); }, // Alias for HTML button

    log: function (msg, type = "info") {
        const div = document.createElement('div');
        const timestamp = new Date().toLocaleTimeString();
        let colorClass = "text-gray-300";
        let icon = ">";

        if (type === "error") { colorClass = "text-red-500"; icon = "!"; }
        if (type === "warning") { colorClass = "text-yellow-400"; icon = "⚠"; }
        if (type === "ai") { colorClass = "text-neon-blue font-bold"; icon = "AZI:"; }

        div.className = `${colorClass} border-l-2 border-gray-700 pl-2`;

        // Markdown benzeri biçimlendirme temizliği
        let cleanMsg = msg.replace(/\*/g, ""); // Yıldızları temizle

        div.innerHTML = `<span class="text-xs text-gray-600">[${timestamp}]</span> <span class="mr-1">${icon}</span> ${cleanMsg}`;

        this.logEl.appendChild(div);
        this.logEl.scrollTop = this.logEl.scrollHeight;
    }
};

// Sayfa yüklendiğinde değil, sekme açıldığında init olması daha iyi ama şimdilik global
// blackbox.js switchView içinden çağrılabilir. 
