// --- CHAT & VOICE SYSTEM ---
let recognition = null;
let isListening = false;

// WebSocket Bağlantısı (Ana Arayüz ile Aynı Protokol)
const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
const wsUrl = `${protocol}${window.location.host}/ws`; // Düzeltildi: /ws endpointini kullan
const ws = new WebSocket(wsUrl);

ws.onopen = () => {
    console.log("AZI NEURAL LINK: CONNECTED");
    const statusOrb = document.querySelector('.orb-core');
    if (statusOrb) statusOrb.style.boxShadow = "0 0 20px #00ff00";
};

ws.onmessage = function (event) {
    const data = JSON.parse(event.data);

    // 1. GEÇMİŞ SENKRONİZASYONU
    if (data.type === "history_sync") {
        // sender: "azi" veya "user"
        const displayName = data.sender === "azi" ? "AZI" : "SEN";
        appendMessage(displayName, data.message);
    }
    // 2. CANLI CEVAPLAR
    else if (data.type === "response" || data.type === "greeting" || data.type === "speak") {
        const msgText = data.text || data.message;

        if (msgText) {
            appendMessage("AZI", msgText);
            speakText(msgText);
        }

        // Aksiyon Kontrolü
        if (data.action) {
            console.log("Action Triggered:", data.action);
            // Burada özel aksiyonlar işlenebilir
        }
    }
};

ws.onclose = () => {
    console.log("AZI NEURAL LINK: DISCONNECTED");
    appendMessage("SİSTEM", "Sunucu bağlantısı koptu. Yeniden bağlanılıyor...");
    setTimeout(() => location.reload(), 3000);
};

function toggleChat() {
    const el = document.getElementById('chatModal');
    el.style.display = el.style.display === 'none' ? 'flex' : 'none';
    if (el.style.display === 'flex') {
        document.getElementById('chatInput').focus();
        scrollToBottom();
    }
}

function scrollToBottom() {
    setTimeout(() => {
        const h = document.getElementById('chatHistory');
        if (h) h.scrollTop = h.scrollHeight;
    }, 100);
}

function appendMessage(sender, text) {
    const h = document.getElementById('chatHistory');
    const div = document.createElement('div');
    div.className = `chat-msg ${sender.toLowerCase()}`;
    div.style.marginBottom = "10px";

    // Stil Ayarlamaları
    let nameColor = '#a8a29e'; // Gri (Default/User)
    let msgColor = '#fff';

    if (sender === 'AZI') {
        nameColor = '#00f2ff'; // Cyan
        msgColor = '#e2e8f0';
    } else if (sender === 'SİSTEM') {
        nameColor = '#ef4444'; // Kırmızı
        msgColor = '#fca5a5';
    }

    // Markdown temizliği (Basit)
    let cleanText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    cleanText = cleanText.replace(/\n/g, '<br>');

    div.innerHTML = `<strong style="color: ${nameColor};">${sender}:</strong> <span style="color: ${msgColor};">${cleanText}</span>`;
    h.appendChild(div);
    scrollToBottom();
}

function sendChat() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;

    // Ekrana hemen yaz (Gecikme hissini önlemek için)
    appendMessage('SEN', text);

    // WebSocket üzerinden gönder
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(text); // DÜZELTME: JSON değil direkt text gönderiyoruz (Main.py beklediği format)
    } else {
        appendMessage('SİSTEM', 'Bağlantı hatası. Lütfen bekleyin.');
    }

    input.value = '';
}

// VOICE RECOGNITION
function toggleRecording() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Tarayıcınız sesli komutu desteklemiyor (Chrome kullanın).");
        return;
    }

    if (isListening) {
        recognition.stop();
        return;
    }

    recognition = new webkitSpeechRecognition();
    recognition.lang = 'tr-TR';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = function () {
        isListening = true;

        // 1. Chat mikrofona yansıt (eğer açıksa)
        const btn = document.getElementById('recordButton');
        if (btn) {
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
            btn.classList.add('blink');
        }

        // 2. ORB görsel geri bildirim (Window kapalıyken anlaşılsın diye)
        const orb = document.querySelector('.orb-core');
        if (orb) orb.style.background = "#ef4444"; // Dinlerken KIRMIZI olsun
    };

    recognition.onend = function () {
        isListening = false;

        const btn = document.getElementById('recordButton');
        if (btn) {
            btn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
            btn.classList.remove('blink');
        }

        const orb = document.querySelector('.orb-core');
        if (orb) orb.style.background = "#00f2ff"; // Normale dön
    };

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('chatInput').value = transcript;
        setTimeout(() => sendChat(), 500); // Otomatik gönder
    };

    recognition.start();
}

// VOICE & TTS
let isSoundOn = true;

function toggleSpeech() {
    isSoundOn = !isSoundOn;
    const btn = document.getElementById('speakToggle');
    if (isSoundOn) {
        btn.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
        btn.style.color = ''; // Reset to default CSS
        btn.title = "Sesli Cevap: AÇIK";
    } else {
        btn.innerHTML = '<i class="fa-solid fa-volume-xmark"></i>';
        btn.style.color = '#777';
        btn.title = "Sesli Cevap: KAPALI";
        // ANINDA SUSTUR
        window.speechSynthesis.cancel();
    }
}

function stopSpeaking() {
    window.speechSynthesis.cancel();
    // Ayrıca görsel konuşma animasyonunu manuel kapat
    const orb = document.querySelector('.orb-core');
    if (orb) orb.style.background = "#00f2ff";

    const orbContainer = document.querySelector('.orb');
    if (orbContainer) orbContainer.classList.remove('speaking');
}

// Sesleri önbelleğe al
let availableVoices = [];
window.speechSynthesis.onvoiceschanged = () => {
    availableVoices = window.speechSynthesis.getVoices();
};

function speakText(text) {
    if (!isSoundOn) return;

    // Stop previous
    window.speechSynthesis.cancel();

    // Sesleri tekrar kontrol et (bazı tarayıcılarda geç yüklenir)
    if (availableVoices.length === 0) {
        availableVoices = window.speechSynthesis.getVoices();
    }

    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'tr-TR';

    // SES KALİTESİ AYARI (EN İYİ *KADIN* SESİ SEÇ)
    // Öncelik: Microsoft Emel (Doğal Kadın) -> Google (Genelde Kadın)
    const bestVoice = availableVoices.find(v => v.lang.includes('tr') && v.name.includes('Emel')) ||
        availableVoices.find(v => v.lang.includes('tr') && v.name.includes('Google')) ||
        availableVoices.find(v => v.lang.includes('tr') && v.name.toLowerCase().includes('female')) ||
        availableVoices.find(v => v.lang.includes('tr'));

    if (bestVoice) {
        utter.voice = bestVoice;
        // console.log("Seçilen Ses:", bestVoice.name);
    }

    // Biraz daha doğal hız
    utter.rate = 0.95;
    utter.pitch = 1.0;

    // Animation Sync
    const orb = document.querySelector('.orb');

    utter.onstart = () => {
        if (orb) orb.classList.add('speaking');
    };

    utter.onend = () => {
        if (orb) orb.classList.remove('speaking');
    };

    window.speechSynthesis.speak(utter);
}

// --- SYSTEM CORE JS ---

// NAVIGATION
function switchView(viewId) {
    // 1. Views
    document.querySelectorAll('.view-panel').forEach(v => v.style.display = 'none');
    const targetEl = document.getElementById(`view-${viewId}`);
    if (targetEl) targetEl.style.display = 'block';

    // 2. Nav Items (Safe Handling)
    document.querySelectorAll('.menu-list li').forEach(li => li.classList.remove('active'));
    // Try to find the nav item that corresponds to this view
    // We look for an onclick that contains the viewId
    const activeNav = Array.from(document.querySelectorAll('.menu-list li')).find(li => {
        return li.getAttribute('onclick')?.includes(`'${viewId}'`) ||
            li.innerHTML.includes(`switchView('${viewId}')`);
    });
    if (activeNav) activeNav.classList.add('active');


    // Header Title
    const titles = {
        'overview': 'GENEL BAKIŞ',
        'factory': 'SİSTEM İNŞA HATTI',
        'licenses': 'AĞ YÖNETİM MERKEZİ',
        'active_cards': 'CANLI İŞLETME DURUMLARI',
        'products': 'YAZILIM ÜRÜNLERİ',
        'city_crm': 'ŞEHİR & HARİTA MERKEZİ',
        'vision': 'AZI GÖRSEL ZEKA',
        'agenda': 'AJANDA & NOTLAR'
    };
    const titleEl = document.getElementById('pageTitle');
    if (titleEl) titleEl.innerText = titles[viewId] || viewId.toUpperCase();

    // Vision Logic
    if (viewId === 'vision') {
        setTimeout(() => {
            if (window.VisionAI) {
                // Init yapılmışsa bile tekrar çağırabiliriz veya kontrol gerekebilir
                // Ama asıl önemli olan startCamera'yı tetiklemek
                window.VisionAI.init(); // Değişkenleri hazırlar
                window.VisionAI.startCamera(); // Kamerayı AÇAR
            }
        }, 100);
    }
    // STOP Camera if leaving vision
    else if (window.VisionAI && window.VisionAI.stream) {
        // VisionAI.stopCamera() would be ideal if it exists, otherwise manual stop
        // Assuming VisionAI handles it or we leave it running (background analysis)
        // For resource saving, we might want to stop it, but user might want badkground processing.
        // Let's leave it for now.
    }

    // Sparklinety CRM Logic
    if (viewId === 'city_crm') {
        setTimeout(() => {
            if (window.CityCRM) {
                if (!CityCRM.map) CityCRM.init();
                if (CityCRM.map) {
                    CityCRM.map.invalidateSize();
                    CityCRM.locateMe(); // Optional: Re-center
                }
            }
        }, 100);

        // Double check for rendering
        setTimeout(() => {
            if (window.CityCRM && CityCRM.map) CityCRM.map.invalidateSize();
        }, 500);
    }

    // Auto-load data
    if (viewId === 'overview') updateStats();
    if (viewId === 'licenses') loadLicenses();
    if (viewId === 'active_cards') loadBusinessCards();
}

// WATCHDOG COOLDOWN
let lastGreetingTime = 0;
const GREETING_COOLDOWN = 30000; // 30 Saniye (Test için düşürdüm)

async function checkWatchdogTriggers(data) {
    console.log("WATCHDOG CHECK:", data);

    // 1. Trigger Voice (Öncelikli Selam)
    if (data.trigger_voice) {
        const now = Date.now();
        if (now - lastGreetingTime > GREETING_COOLDOWN) {
            lastGreetingTime = now;
            console.log("WATCHDOG SPEAKING:", data.trigger_voice);
            speakText(data.trigger_voice);
            appendMessage('AZI', data.trigger_voice);
            return; // Selam verdiyse analizi okumasın
        }
    }

    // 2. CHECK BRAIN STREAM (Proactive Voice)
    if (!data.trigger_voice) {
        try {
            const resBrain = await fetch('/api/brain/stream');
            const brainData = await resBrain.json();

            if (brainData.speak) {
                console.log("AZI BRAIN PROACTIVE:", brainData.speak);

                // Show in chat as well
                appendMessage('AZI', brainData.speak);

                // Speak
                speakText(brainData.speak);
                return;
            }
        } catch (e) {
            console.log("Brain stream check failed:", e);
        }
    }

    // 3. Analysis Reading (Fallback)
    if (data.analysis && window.VisionAI && window.VisionAI.isAutoMode) {
        // speakText(data.analysis); // Optional
    }
}
// CARD VIEW LOGIC - (Kept as is)
// ... (Lines 309-778 kept implicitly by not replacing them) ...
// Use replace_file_content carefully. 
// I will only replace switchView and checkWatchdogTriggers section if I can target precisely.
// Given strict contiguous rule, and that switchView is 204-260, and checkWatchdogTriggers is 267-307.
// I will replace from 204 to 822 (Connection Watchdog) in chunks or just switchView?
// No, I can use multi_replace? No, standard is replace_file_content for single block.
// I will target switchView first. Then Watchdog.
// Wait, the ReplacementContent above is huge.
// Let's just do switchView first.


// WATCHDOG COOLDOWN

// CARD VIEW LOGIC
async function loadBusinessCards() {
    const grid = document.getElementById('business-cards-grid');
    grid.innerHTML = '<div class="text-center w-full col-span-4 text-gray-500">Sinyal taranıyor...</div>';

    try {
        const res = await fetch('/api/telemetry/cards');
        const cards = await res.json();

        if (cards.length === 0) {
            grid.innerHTML = '<div class="text-center w-full col-span-4 text-gray-500">Ağda aktif node bulunamadı.</div>';
            return;
        }

        grid.innerHTML = cards.map(c => `
            <div class="modern-card">
                <button class="btn-delete-card" onclick="event.stopPropagation(); deleteLicense(${c.id})" title="Sil">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
                <button class="btn-manage-card" onclick="event.stopPropagation(); openCommandModal(${c.id})" title="Yönet">
                    <i class="fa-solid fa-gamepad"></i>
                </button>

                <div class="mc-header">
                    <div class="mc-title-group">
                        <span class="mc-subtitle">${c.type.toUpperCase()}</span>
                        <div class="mc-title">${c.name}</div>
                    </div>
                </div>

                <div class="mc-body">
                    <!-- Status Row -->
                    <div class="mc-row">
                        <div class="mc-label"><i class="fa-solid fa-signal mc-icon text-blue-400"></i> Durum</div>
                        <div class="mc-badge ${!c.is_online ? 'offline' : ''}">${c.is_online ? 'ONLINE' : 'OFFLINE'}</div>
                    </div>

                    <!-- License Row -->
                    <div class="mc-row">
                        <div class="mc-label"><i class="fa-solid fa-key mc-icon text-gray-400"></i> Lisans</div>
                        <div class="mc-value">${c.license_key.substring(0, 8)}...</div>
                    </div>

                    <!-- Time Row -->
                    <div class="mc-row">
                        <div class="mc-label"><i class="fa-regular fa-clock mc-icon text-yellow-400"></i> Son Sinyal</div>
                        <div class="mc-value yellow">${new Date(c.last_seen).toLocaleTimeString()}</div>
                    </div>

                     <!-- Alert Row -->
                    ${c.alert_message ? `
                    <div class="mc-row">
                         <div class="mc-label text-red-400"><i class="fa-solid fa-triangle-exclamation mc-icon"></i> Uyarı</div>
                         <div class="mc-value text-red-500 text-xs">${c.alert_message}</div>
                    </div>` : ''}
                </div>

                <div class="mc-footer">
                    <div class="mc-footer-label">Günlük Ciro</div>
                    <div class="mc-footer-value">₺${c.today_revenue.toLocaleString('tr-TR')}</div>
                </div>
            </div>
        `).join('');

    } catch (e) {
        console.error(e);
        grid.innerHTML = `<div class="text-center text-red-500 col-span-4">
            <p class="font-bold">Telemetri Verisi Alınamadı</p>
            <p class="text-xs text-gray-400 mt-2">${e.message}</p>
        </div>`;
    }
}

// CLOCK
setInterval(() => {
    document.getElementById('clock').innerText = new Date().toLocaleTimeString();
}, 1000);

// --- WIZARD LOGIC ---
let wizardData = {
    name: '',
    type: 'stock',
    personnel: 10,
    products: 500
};

function updateRangeIds() {
    wizardData.personnel = document.getElementById('wizPersonnel').value;
    wizardData.products = document.getElementById('wizProducts').value;
    document.getElementById('lblPersonnel').innerText = wizardData.personnel;
    document.getElementById('lblProducts').innerText = wizardData.products;
}

function nextStep(step) {
    if (step === 2) {
        const name = document.getElementById('wizName').value;
        if (!name) { alert("LÜTFEN İŞLETME ADI GİRİNİZ."); return; }
        wizardData.name = name;
        wizardData.type = document.getElementById('wizType').value;
    }

    // UI Updates
    document.querySelectorAll('.step-panel').forEach(p => p.style.display = 'none');
    document.getElementById(`step-${step}`).style.display = 'block';

    document.querySelectorAll('.wizard-steps .step').forEach(s => s.classList.remove('active'));
    document.getElementById(`step${step}-marker`).classList.add('active');
}

function prevStep(step) {
    document.querySelectorAll('.step-panel').forEach(p => p.style.display = 'none');
    document.getElementById(`step-${step}`).style.display = 'block';

    document.querySelectorAll('.wizard-steps .step').forEach(s => s.classList.remove('active'));
    document.getElementById(`step${step}-marker`).classList.add('active');
}

function toggleCustomReq() {
    const type = document.getElementById('wizType').value;
    const area = document.getElementById('custom-req-area');
    if (type === 'custom') {
        area.style.display = 'block';
    } else {
        area.style.display = 'none';
        document.getElementById('wizCustomReq').value = '';
    }
    wizardData.type = type;
}

async function startPackaging() {
    nextStep(3); // Show terminal
    const log = document.getElementById('buildLog');
    const bar = document.getElementById('buildProgress');

    log.innerHTML += "<br>> INITIATING CORE BUILD PROTOCOL...";
    bar.style.width = "20%";

    // 1. Create License
    try {
        log.innerHTML += "<br>> REGISTERING BUSINESS IDENTITY...";

        const payload = {
            name: wizardData.name,
            product_type: wizardData.type,
            details: {
                personnel: parseInt(wizardData.personnel),
                products: parseInt(wizardData.products),
                custom_requirements: document.getElementById('wizCustomReq').value
            },
            price: parseFloat(document.getElementById('wiz-price').value || 0)
        };

        // Eğer CUSTOM seçildiyse ama açıklama girilmediyse uyar
        if (wizardData.type === 'custom' && !payload.details.custom_requirements) {
            alert("LÜTFEN SORUN VE İHTİYAÇ TANIMINI GİRİNİZ.");
            nextStep(2); // Geri git
            return;
        }

        const resCreate = await fetch('/api/license/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const dataCreate = await resCreate.json();

        if (dataCreate.status !== "created") throw new Error("License creation failed: " + (dataCreate.detail || "Unknown error"));

        log.innerHTML += `<br>> LICENSE GENERATED: ${dataCreate.license_key}`;
        bar.style.width = "50%";

        // 2. Package
        log.innerHTML += "<br>> INJECTING CONFIG INTO EXECUTABLE...";
        const resPack = await fetch(`/api/factory/package/${dataCreate.license_key}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_type: wizardData.type,
                business_name: wizardData.name,
                custom_requirements: document.getElementById('wizCustomReq').value
            })
        });
        const dataPack = await resPack.json();

        if (!dataPack.success) throw new Error(dataPack.error);

        bar.style.width = "100%";
        log.innerHTML += "<br>> PACKAGING COMPLETE. READY FOR DEPLOYMENT.";

        // Show Download
        document.getElementById('downloadLink').href = dataPack.download_url;
        document.getElementById('downloadArea').style.display = 'block';

    } catch (e) {
        log.innerHTML += `<br>> FATAL ERROR: ${e}`;
        bar.style.backgroundColor = "red";
    }
}

function resetWizard() {
    document.getElementById('wizName').value = '';
    document.getElementById('downloadArea').style.display = 'none';
    document.getElementById('buildProgress').style.width = '0%';
    document.getElementById('buildLog').innerHTML = "> SYSTEM INIT... OK<br>> MASTER ENGINE LOCATED... OK";
    nextStep(1);
}

// --- DATA LOGIC ---
// currentBusinesses is declared in licenses.js


// function loadLicenses() removed. Delegated to licenses.js

function openDetails(id) {
    const b = currentBusinesses.find(x => x.id === id);
    if (!b) return;

    document.getElementById('cardName').innerText = b.name;
    document.getElementById('cardLicense').innerText = b.license_key;
    document.getElementById('cardStatus').innerText = b.is_online ? "ONLINE" : "OFFLINE";
    document.getElementById('cardLastSeen').innerText = b.last_seen || "Yok";

    // System Info
    try {
        const sys = JSON.parse(b.system_info || '{}');
        document.getElementById('cardSystemInfo').innerText = Object.keys(sys).length ? JSON.stringify(sys, null, 2) : "Telemetry data waiting...";
    } catch { document.getElementById('cardSystemInfo').innerText = "Data Error"; }

    // Business Details
    try {
        const det = JSON.parse(b.details || '{}');
        document.getElementById('cardDetailsInfo').innerText = Object.keys(det).length ? JSON.stringify(det, null, 2) : "No managed capacity data.";
    } catch { document.getElementById('cardDetailsInfo').innerText = "Data Error"; }

    document.getElementById('businessDetailsModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('businessDetailsModal').style.display = 'none';
}

// --- COMMAND CENTER LOGIC ---
let currentTargetLicense = null;

function openCommandModal(id) {
    const b = currentBusinesses.find(x => x.id === id);
    if (!b) return;

    currentTargetLicense = b.license_key;
    document.getElementById('cmdTargetName').innerText = b.name;
    document.getElementById('cmdTargetLicense').innerText = b.license_key;

    document.getElementById('commandModal').style.display = 'flex';
}

function closeCommandModal() {
    document.getElementById('commandModal').style.display = 'none';
    currentTargetLicense = null;
}

async function sendCommand(type) {
    if (!currentTargetLicense) return;

    let payload = {
        license_key: currentTargetLicense,
        command: type,
        args: {}
    };

    if (type === 'popup') {
        const msg = document.getElementById('cmdMessageInput').value;
        if (!msg) { alert("Mesaj boş olamaz!"); return; }
        payload.args = { title: "MERKEZ NOTU", msg: msg };
    }
    else if (type === 'open_url') {
        const url = document.getElementById('cmdUrlInput').value;
        if (!url) { alert("URL boş olamaz!"); return; }
        payload.args = { url: url };
    }
    else if (type === 'shutdown' || type === 'lock') {
        if (!confirm("BU İŞLEM KRİTİKTİR. ONAYLIYOR MUSUNUZ?")) return;
    }

    try {
        const res = await fetch('/api/control/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (data.status === 'queued') {
            alert("Komut Kuyruğa Eklendi! (Hedef Cihaz İlk Sinyalde Alacak)");
            closeCommandModal();
        } else {
            alert("Hata: " + JSON.stringify(data));
        }

    } catch (e) {
        alert("Bağlantı Hatası: " + e);
    }
}

// --- LICENSE ACTIONS ---
async function deleteLicense(id) {
    if (!confirm("BU LİSANSI VE İLGİLİ İŞLETME VERİLERİNİ KALICI OLARAK SİLMEK İSTEDİĞİNİZE EMİN MİSİNİZ?")) return;

    try {
        const res = await fetch(`/api/license/${id}`, { method: 'DELETE' });
        const data = await res.json();

        if (data.success) {
            // alert("Lisans Silindi."); // Kullanıcıyı yormayalım, direkt güncelleyelim.
            loadLicenses(); // Tabloyu yenile (licenses.js içinde olmalı)
            loadBusinessCards(); // Kartları yenile
            updateStats(); // İstatistikleri yenile
        } else {
            alert("Silme Hatası: " + (data.detail || "Bilinmiyor"));
        }
    } catch (e) {
        alert("Bağlantı Hatası: " + e);
    }
}

async function deleteAllLicenses() {
    if (!confirm("⚠️ TÜM AĞI SIFIRLAMAK ÜZERESİNİZ!\n\nBu işlem tüm kayıtlı işletmeleri, lisans anahtarlarını ve verileri silecektir.\n\nOnaylıyor musunuz?")) return;

    // Güvenlik için ikinci onay
    if (!confirm("Son Kararınız mı? Bu işlem geri alınamaz.")) return;

    try {
        // Tek tek silmek yerine reset endpoint'i varsa onu kullanmak daha iyi olur ama şimdilik ID'leri toplayıp silelim veya backend'e reset ekleyelim.
        // Backend'de reset_db.py var ama API endpoint var mı?
        // API listesinde /api/license/{id} var.

        // currentBusinesses licenses.js'den geliyor.
        if (!window.currentBusinesses || window.currentBusinesses.length === 0) {
            alert("Silinecek veri yok.");
            return;
        }

        let count = 0;
        for (let b of window.currentBusinesses) {
            await fetch(`/api/license/${b.id}`, { method: 'DELETE' });
            count++;
        }

        alert(`${count} Adet İşletme Ağdan Silindi.`);
        location.reload();

    } catch (e) {
        alert("Toplu Silme Hatası: " + e);
    }
}

// Init
updateStats();

let sparklineChart = null;
let revenueChart = null; // Global reference

async function updateStats() {
    loadLicenses(); // Refresh node list

    try {
        // --- 1. SYSTEM HEALTH & TOTALS ---
        // Aslında 'loadLicenses' api/businesses çağırıyor ve 'currentBusinesses'ı dolduruyor.
        // Oradan aktif node sayısını alabiliriz.
        // Ancak daha gelişmiş analiz için endpoint'e soralım.
        const resHealth = await fetch('/api/analysis/health');
        const healthData = await resHealth.json();

        // Aktif Node Güncelleme
        const elActive = document.getElementById('statActiveNodes');
        if (elActive) elActive.innerText = healthData.active + "/" + healthData.total;

        // Daire doluluk
        const percent = healthData.total > 0 ? (healthData.active / healthData.total) * 100 : 0;
        const circle = document.querySelector('.circle');
        if (circle) {
            circle.style.strokeDasharray = `${percent}, 100`;
            circle.style.stroke = healthData.score > 50 ? '#22c55e' : (healthData.score > 20 ? '#facc15' : '#ef4444');
        }

        // --- 2. REVENUE TRENDS (REAL) ---
        const resTrends = await fetch('/api/analysis/trends');
        const trendsData = await resTrends.json(); // [{date: '...', revenue: 100}, ...]

        // Toplam Ciro (Son 7 Günlük)
        const total7DayRev = trendsData.reduce((acc, curr) => acc + curr.revenue, 0);
        const elRev = document.getElementById('dash-total-revenue');
        // if (elRev) elRev.innerText = `₺${total7DayRev.toLocaleString('tr-TR')}`; 
        // Kullanıcı lisans bedelini değil, ciro akışını görmek istiyor sanırım.
        // Ama şimdilik 'Lisans Geliri'ni mi yoksa 'İşletme Cirolarını' mı gösteriyoruz?
        // 'Total Ciro' genelde Azi'nin kazancıdır. Ama analizde işletme cirolarını topluyoruz.
        // Neyse, trendsData işletme ciroları toplamıdır.
        if (elRev) elRev.innerText = `₺${total7DayRev.toLocaleString('tr-TR')}`;


        // Sparkline Güncelleme
        if (sparklineChart) {
            // Son 7 gün verisini kullan
            const sparkValues = trendsData.map(d => d.revenue);
            // Eğer veri azsa 0 ile doldur
            while (sparkValues.length < 7) sparkValues.unshift(0);

            sparklineChart.data.datasets[0].data = sparkValues;
            sparklineChart.update();
        }

        // Main Chart Güncelleme (Revenue Only for now)
        if (revenueChart) {
            const labels = trendsData.map(d => d.date); // '2023-10-25'
            const values = trendsData.map(d => d.revenue);

            revenueChart.data.labels = labels;
            revenueChart.data.datasets[0].data = values.map(v => v / 100); // Küçük bar (Traffic simülasyonu yerine) veya scale et
            revenueChart.data.datasets[1].data = values; // Çizgi (Revenue)
            revenueChart.update();
        }

    } catch (e) {
        console.error("Stats Update Error:", e);
        addLogEntry("> ERROR SYNCING ANALYTICS DATA");
    }

    // Refresh Loop
    setTimeout(updateStats, 10000); // 10 saniyede bir
}

// Log Helper
function addLogEntry(msg) {
    const logBox = document.getElementById('dashboard-log');
    if (logBox) {
        const time = new Date().toLocaleTimeString();
        logBox.innerHTML += `<br><span style="color:#666">[${time}]</span> ${msg}`;
        const lines = logBox.innerHTML.split('<br>');
        if (lines.length > 8) logBox.innerHTML = lines.slice(-8).join('<br>');
    }
}


// Charts Init
document.addEventListener('DOMContentLoaded', () => {
    // Sparkline
    const ctxSpark = document.getElementById('sparklineRevenue');
    if (ctxSpark) {
        sparklineChart = new Chart(ctxSpark, {
            type: 'line',
            data: {
                labels: Array(7).fill(''),
                datasets: [{
                    data: [0, 0, 0, 0, 0, 0, 0],
                    borderColor: '#00f2ff',
                    borderWidth: 1,
                    pointRadius: 2,
                    fill: false,
                    tension: 0.2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: true } },
                scales: { x: { display: false }, y: { display: false } }
            }
        });
    }



    // --- CONNECTION WATCHDOG ---
    window.ConnectionWatchdog = {
        isOnline: true,
        overlay: null,

        init: function () {
            this.overlay = document.createElement('div');
            this.overlay.className = 'connection-overlay';
            this.overlay.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85); z-index: 9999;
            display: none; align-items: center; justify-content: center;
            flex-direction: column; color: #ef4444; font-family: 'Rajdhani', sans-serif;
        `;
            this.overlay.innerHTML = `
            <i class="fa-solid fa-satellite-dish fa-spin" style="font-size: 3rem; margin-bottom: 20px;"></i>
            <h2 style="font-size: 2rem;">SİNYAL KAYBI</h2>
            <p>AZI SERVER BAĞLANTISI KOPTU. YENİDEN KURULUYOR...</p>
        `;
            document.body.appendChild(this.overlay);
            setInterval(() => this.check(), 5000);
        },

        check: async function () {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 2000);
                const res = await fetch('/api/system/version', { signal: controller.signal });
                clearTimeout(timeoutId);
                if (res.ok) {
                    if (!this.isOnline) {
                        this.isOnline = true;
                        this.overlay.style.display = 'none';
                        updateStats();
                    }
                } else { throw new Error("500"); }
            } catch (e) {
                if (this.isOnline) {
                    this.isOnline = false;
                    this.overlay.style.display = 'flex';
                }
            }
        }
    };

    window.Agenda = {
        currentDate: new Date(),
        selectedDate: null,
        notes: {}, // { 'YYYY-MM-DD': 'Note content' }

        init: function () {
            // Load from storage
            const stored = localStorage.getItem('azi_agenda_notes');
            if (stored) this.notes = JSON.parse(stored);

            // Select today
            this.selectedDate = new Date();
            this.renderCalendar();
            this.renderNote();
            this.renderDashboardWidget();
        },

        prevMonth: function () {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.renderCalendar();
        },

        nextMonth: function () {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.renderCalendar();
        },

        renderCalendar: function () {
            const year = this.currentDate.getFullYear();
            const month = this.currentDate.getMonth();

            // Update Header
            const monthNames = ["OCAK", "ŞUBAT", "MART", "NİSAN", "MAYIS", "HAZİRAN", "TEMMUZ", "AĞUSTOS", "EYLÜL", "EKİM", "KASIM", "ARALIK"];
            document.getElementById('agenda-month-year').innerText = `${monthNames[month]} ${year}`;

            const grid = document.getElementById('agenda-calendar-grid');
            grid.innerHTML = '';

            const firstDay = new Date(year, month, 1).getDay(); // 0=Sun, 1=Mon...
            const daysInMonth = new Date(year, month + 1, 0).getDate();

            // Adjust for Monday start (0=Sun -> 6, 1=Mon -> 0)
            let startCol = firstDay === 0 ? 6 : firstDay - 1;

            // Blanks
            for (let i = 0; i < startCol; i++) {
                grid.innerHTML += `<div class="p-2"></div>`;
            }

            // Days
            const todayStr = new Date().toISOString().split('T')[0]; // YYYY-MM-DD

            for (let d = 1; d <= daysInMonth; d++) {
                const dateObj = new Date(year, month, d);
                // Local ISO Check (Avoid timezone issues roughly)
                const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;

                const hasNote = this.notes[dateStr] && this.notes[dateStr].trim().length > 0;
                const isToday = dateStr === todayStr;
                const isSelected = this.selectedDate &&
                    this.selectedDate.getFullYear() === year &&
                    this.selectedDate.getMonth() === month &&
                    this.selectedDate.getDate() === d;

                let classes = "p-4 border border-gray-800 text-center cursor-pointer hover:bg-gray-800 transition relative h-24 flex flex-col justify-between";
                if (isToday) classes += " bg-gray-600/30 border-blue-500";
                if (isSelected) classes += " bg-blue-900/50 border-blue-400 text-white shadow-[0_0_15px_rgba(59,130,246,0.3)]";

                // Note Indicator
                let indicator = hasNote ? `<i class="fa-solid fa-note-sticky text-yellow-400 text-xs absolute top-2 right-2"></i>` : '';

                grid.innerHTML += `
                <div class="${classes}" onclick="Agenda.selectDay(${year}, ${month}, ${d})">
                    <span class="text-lg font-bold ${isToday ? 'text-blue-400' : 'text-gray-400'}">${d}</span>
                    ${indicator}
                </div>
            `;
            }
        },

        selectDay: function (y, m, d) {
            this.selectedDate = new Date(y, m, d);
            this.renderCalendar(); // Re-render to show selection highlight
            this.renderNote();
        },

        renderNote: function () {
            if (!this.selectedDate) return;

            const dateStr = this.formatDateKey(this.selectedDate);
            document.getElementById('selected-date-display').innerText = this.selectedDate.toLocaleDateString('tr-TR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

            document.getElementById('agenda-note-input').value = this.notes[dateStr] || '';
        },

        saveNote: function () {
            if (!this.selectedDate) return;

            const dateStr = this.formatDateKey(this.selectedDate);
            const content = document.getElementById('agenda-note-input').value;

            if (content.trim() === '') {
                delete this.notes[dateStr];
            } else {
                this.notes[dateStr] = content;
            }

            localStorage.setItem('azi_agenda_notes', JSON.stringify(this.notes));

            // Visual Feedback
            const btn = document.querySelector('#view-agenda button[onclick="Agenda.saveNote()"]');
            const originalHtml = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-check"></i> KAYDEDİLDİ';
            setTimeout(() => btn.innerHTML = originalHtml, 1500);

            this.renderCalendar(); // Update indicators
            this.renderDashboardWidget();
        },

        renderDashboardWidget: function () {
            const container = document.getElementById('dashboard-agenda-preview');
            if (!container) return; // Might not be on overview page

            // Find upcoming notes (today + 7 days)
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            let upcoming = [];
            const sortedDates = Object.keys(this.notes).sort();

            for (let dStr of sortedDates) {
                const d = new Date(dStr);
                // Simple check: is it today or future?
                if (d >= today) {
                    // Get first line as summary
                    const summary = this.notes[dStr].split('\n')[0].substring(0, 25) + (this.notes[dStr].length > 25 ? '...' : '');
                    upcoming.push({ date: d, text: summary });
                }
            }

            if (upcoming.length === 0) {
                container.innerHTML = `<div class="text-xs text-gray-500 italic mt-2 text-center">Planlanmış not yok.</div>`;
            } else {
                container.innerHTML = upcoming.slice(0, 3).map(item => `
                <div class="flex items-center gap-2 mb-2 text-xs text-gray-300">
                    <span class="w-2 h-2 rounded-full ${item.date.getTime() === today.getTime() ? 'bg-yellow-400 animate-pulse' : 'bg-blue-500'}"></span>
                    <span class="font-bold text-gray-500 w-12">${item.date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })}</span>
                    <span class="truncate">${item.text}</span>
                </div>
            `).join('');
            }
        },

        formatDateKey: function (date) {
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
        }
    };

    // Initialize Global Objects
    window.Agenda.init();
    window.ConnectionWatchdog.init();
});
