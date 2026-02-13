window.toggleVoice = function () {
    console.log("toggleVoice Called");
    // Toggle State
    let currentState = localStorage.getItem("speechEnabled") === "true";
    let newState = !currentState;

    // Save
    localStorage.setItem("speechEnabled", newState);
    console.log("New State:", newState);

    // Update UI
    updateVoiceButton();
};

function updateVoiceButton() {
    console.log("Updating Voice Button...");
    const btn = document.getElementById("voiceBtn");

    // Check localStorage again to be sure
    let isEnabled = localStorage.getItem("speechEnabled") === "true";

    if (btn) {
        if (isEnabled) {
            // AÇIK DURUM: Parlak Arkaplan
            btn.style.borderColor = "#00ffcc";
            btn.style.backgroundColor = "rgba(0, 255, 204, 0.2)"; // Hafif dolgu
            btn.style.color = "#00ffcc";
            btn.style.boxShadow = "0 0 15px rgba(0, 255, 204, 0.4)";
            btn.innerHTML = "🔊 SES: AÇIK";
            btn.style.fontWeight = "bold";
        } else {
            // KAPALI DURUM: Sönük
            btn.style.borderColor = "#444";
            btn.style.backgroundColor = "transparent";
            btn.style.color = "#666";
            btn.style.boxShadow = "none";
            btn.innerHTML = "🔇 SES: KAPALI";
            btn.style.fontWeight = "normal";
        }
    } else {
        console.warn("Voice Button not found in DOM");
    }
}

// Initial Call
document.addEventListener("DOMContentLoaded", () => {
    updateVoiceButton();
});

const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
// const voiceBtn = document.getElementById("voiceBtn"); // Removed duplicate ref
const messagesDiv = document.getElementById("messages");

// SES AYARLARI eski kod silindi çünkü yukarı taşındı

// WebSocket Bağlantısı
// WebSocket Bağlantısı
// config.js ile tanımlanan global WS_BASE kullanılır
const wsUrl = window.WS_BASE || "ws://localhost:8001/ws";
const ws = new WebSocket(wsUrl);

const statusSpan = document.querySelector(".status span");
const statusDiv = document.querySelector(".status");

ws.onopen = function () {
    console.log("WS Connected via", wsUrl);
    if (statusSpan) {
        // Show if connected to Render or Local
        const target = wsUrl.includes("localhost") || wsUrl.includes("127.0.0.1") ? "LOCAL" : "ONLINE";
        statusSpan.innerText = target;
        statusSpan.style.color = "#00ffcc";
        statusSpan.style.textShadow = "0 0 10px #00ffcc";
        statusSpan.classList.remove("blink");

        // Add Host info tooltip
        statusDiv.title = "Connected to: " + wsUrl;
    }
};

ws.onclose = function () {
    console.log("WS Disconnected");
    if (statusSpan) {
        statusSpan.innerText = "OFFLINE";
        statusSpan.style.color = "red";
        statusSpan.style.textShadow = "0 0 10px red";
        statusSpan.classList.add("blink");
    }
};

ws.onmessage = function (event) {
    const data = JSON.parse(event.data);

    // Mesaj Tipleri
    if (data.type === "history_sync") {
        // Geçmiş mesajları ekle
        addMessage(data.sender, data.message);
    }
    else if (data.type === "greeting" || data.type === "response" || data.type === "alert") {
        addMessage("azi", data.message);

        // SESLİ YANIT (TTS)
        let isSpeechEnabled = localStorage.getItem("speechEnabled") === "true";
        if (isSpeechEnabled) {
            if (data.audio_url) {
                // Sunucudan gelen ses (gTTS)
                console.log("Playing server audio:", data.audio_url);
                const audio = new Audio(data.audio_url);
                audio.play();
            } else {
                // Fallback: Tarayıcı sesi (Offline)
                // Sadece kısa metinler için (uzun metinler sıkıcı olabilir)
                if (data.message && data.message.length < 200) {
                    speakTextFallback(data.message);
                }
            }
        }

        // Aksiyon Kontrolü
        if (data.action === "open_blackbox") {
            setTimeout(() => {
                window.location.href = "blackbox.html";
            }, 1000);
        }
        else if (data.action === "open_blackbox_fast") {
            // 1. KIRMIZI GÖZ EFEKTİ (Hemen)
            enableRedAlert();

            // 2. BÜYÜME VE GEÇİŞ EFEKTİ
            setTimeout(() => {
                const eyeContainer = document.querySelector(".ai-eye-container");
                if (eyeContainer) {
                    eyeContainer.classList.add("zoom-out");
                }
            }, 500); // Kırmızı olduktan yarım saniye sonra büyümeye başla

            // 3. YÖNLENDİRME (3 Saniye Sonra)
            setTimeout(() => {
                window.location.href = "blackbox.html";
            }, 3500); // 0.5s bekle + 3s büyüme = 3.5s
        }
        else if (data.action === "open_investment_deck") {
            // YATIRIM SUNUMU AÇILIŞI
            setTimeout(() => {
                window.open("investment.html", "_blank"); // Yeni sekmede açmak daha güvenli olabilir sunum için
            }, 1000);
        }
        else if (data.action === "open_stock_deck") {
            // STOK ÜRÜN SUNUMU
            setTimeout(() => {
                window.open("ac_stock.html", "_blank");
            }, 1000);
        }
        else if (data.action === "open_staff_deck") {
            // STOK ÜRÜN SUNUMU
            setTimeout(() => {
                window.open("ac_staff.html", "_blank");
            }, 1000);
        }
        else if (data.action === "open_emlak_deck") {
            // EMLAK SUNUMU
            setTimeout(() => {
                window.open("ac_emlak.html", "_blank");
            }, 1000);
        }
    }
};

function enableRedAlert() {
    const outerRing = document.querySelector(".eye-ring.outer");
    const innerRing = document.querySelector(".eye-ring.inner");
    const core = document.querySelector(".eye-core");
    const statusText = document.querySelector(".ai-status-text");

    if (outerRing) outerRing.classList.add("red-alert");
    if (innerRing) innerRing.classList.add("red-alert");
    if (core) core.classList.add("red-alert");

    if (statusText) {
        statusText.innerText = "YETKİLİ ERİŞİMİ";
        statusText.classList.add("red-alert-text");
    }
}

function speakTextFallback(text) {
    if (!window.speechSynthesis) return;

    // Temizle (Markdown ve HTML taglerini kaldır)
    let cleanText = text.replace(/<[^>]*>/g, "").replace(/[*#_`]/g, "");

    window.speechSynthesis.onvoiceschanged = () => {
        // Sesler yüklendiğinde tetiklenir (Chrome mobilde bazen geç yüklenir)
    };

    const voices = window.speechSynthesis.getVoices();
    // Türkçe ve Mümkünse Erkek sesi bulmaya çalış
    // "Google Türkçe" genelde kadın, ama "Yelda" veya "Cem" (iOS) olabilir ??
    // Android'de genelde tek ses var.

    let selectedVoice = voices.find(v => v.lang.includes("tr") && (v.name.includes("Male") || v.name.includes("Erkek") || v.name.includes("Cem")));
    if (!selectedVoice) {
        selectedVoice = voices.find(v => v.lang.includes("tr"));
    }

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = "tr-TR";
    if (selectedVoice) {
        utterance.voice = selectedVoice;
    }
    // Hızı biraz artır (Yavaş dediği için)
    utterance.rate = 1.1;

    window.speechSynthesis.speak(utterance);
}

function sendMessage() {
    const text = userInput.value.trim();
    if (text) {
        addMessage("user", text);
        ws.send(text);
        userInput.value = "";
    }
}

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

function addMessage(sender, text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}`;

    // Güvenli HTML ve Link Formatlama
    let content = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    content = content.replace(/\n/g, "<br>");
    content = content.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');

    // SVG AVATARLAR (Boyut Garantili)
    const aziAvatar = `<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#00ffcc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>`;
    const userAvatar = `<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`;

    const avatarHtml = sender === 'azi' ? aziAvatar : userAvatar;

    msgDiv.innerHTML = `
        <div class="avatar">${avatarHtml}</div>
        <div class="content">${content}</div>
    `;

    messagesDiv.appendChild(msgDiv);
    scrollToBottom(msgDiv);
}

function scrollToBottom(element) {
    // Yöntem 1: Yeni eklenen elemana odaklan (En modem ve güvenli yol)
    if (element) {
        setTimeout(() => {
            element.scrollIntoView({ behavior: "smooth", block: "end" });
        }, 100);
    }

    // Yöntem 2: Kutuyu en alta zorla (Yedek)
    setTimeout(() => {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }, 150);
}

// --- SESLİ KOMUT (WEB SPEECH API) ---
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.lang = 'tr-TR';
    recognition.interimResults = false;

    micBtn.addEventListener('click', () => {
        if (micBtn.classList.contains('listening')) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });

    recognition.onstart = () => {
        micBtn.classList.add('listening');
        userInput.placeholder = "Dinliyorum...";
    };

    recognition.onend = () => {
        micBtn.classList.remove('listening');
        userInput.placeholder = "Bir komut yazın...";
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        setTimeout(sendMessage, 800);
    };

    recognition.onerror = (event) => {
        console.error("Ses hatası:", event.error);
        micBtn.classList.remove('listening');
    };
} else {
    // Mobil veya desteklenmeyen tarayıcılar için butonu gizle
    if (micBtn) micBtn.style.display = 'none';
}

// --- LOGIN MODAL LOGIC ---
const blackboxBtn = document.getElementById("blackboxBtn");
const loginModal = document.getElementById("loginModal");
const closeModal = document.querySelector(".close-modal");
const passwordInput = document.getElementById("passwordInput");
const loginConfirm = document.getElementById("loginConfirm");
const loginError = document.getElementById("loginError");

if (blackboxBtn && loginModal) {
    blackboxBtn.addEventListener("click", () => {
        loginModal.style.display = "block";
        passwordInput.value = "";
        passwordInput.focus();
        loginError.innerText = "";
    });

    closeModal.addEventListener("click", () => {
        loginModal.style.display = "none";
    });

    window.addEventListener("click", (event) => {
        if (event.target == loginModal) {
            loginModal.style.display = "none";
        }
    });

    function checkPassword() {
        if (!passwordInput) return;
        const pass = passwordInput.value;
        if (pass === "9246") {
            loginError.innerText = "ERİŞİM ONAYLANDI";
            loginError.style.color = "#00ffcc";
            setTimeout(() => {
                window.location.href = "blackbox.html";
            }, 800);
        } else {
            loginError.innerText = "HATALI ŞİFRE";
            loginError.style.color = "red";
            passwordInput.value = "";
        }
    }

    if (loginConfirm) loginConfirm.addEventListener("click", checkPassword);
    if (passwordInput) passwordInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") checkPassword();
    });
}
