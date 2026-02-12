// --- AZI MOBILE CORE ---

// CONFIG
const API_URL = window.API_BASE || window.location.origin + '/api';

// STATE
let isListening = false;
let isSpeaking = false;
let watchId = null;

// DOM ELEMENTS
const micBtn = document.getElementById('micBtn');
const chatLog = document.getElementById('chatLog');
const statServer = document.getElementById('stat-server');
const statGps = document.getElementById('stat-gps');
const gpsCoords = document.getElementById('gps-coords');

// --- 1. VOICE RECOGNITION (STT) ---
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.lang = 'tr-TR';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
        isListening = true;
        micBtn.classList.add('listening');
        addLog("Listening...", "sys");
    };

    recognition.onend = () => {
        isListening = false;
        micBtn.classList.remove('listening');
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        addLog(transcript, "user");
        processCommand(transcript);
    };

    recognition.onerror = (event) => {
        console.error("Speech Error:", event.error);
        addLog("Error: " + event.error, "sys");
        micBtn.classList.remove('listening');

        if (event.error === 'not-allowed' || event.error === 'security') {
            document.getElementById('perm-help').style.display = 'block';
        }
    };
} else {
    alert("Tarayıcınız ses tanımayı desteklemiyor (Chrome kullanın).");
}

} else {
    alert("Tarayıcınız ses tanımayı desteklemiyor (Chrome kullanın).");
}

micBtn.addEventListener('click', () => {
    if (isSpeaking) {
        window.speechSynthesis.cancel();
        isSpeaking = false;
        micBtn.classList.remove('speaking');
        return;
    }
    if (isListening) recognition.stop();
    else recognition.start();
});

// --- VISION (CAMERA) ---
const camBtn = document.getElementById('camBtn');
const cameraInput = document.getElementById('cameraInput');

camBtn.addEventListener('click', () => {
    cameraInput.click();
});

cameraInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    addLog("Analyzing Image...", "sys");

    // Convert to Base64
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = async () => {
        const base64Image = reader.result;

        try {
            const res = await fetch(`${API_URL}/vision_scan`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: base64Image,
                    prompt: "Bu fotoğrafta ne görüyorsun? Detaylı anlat."
                })
            });

            const data = await res.json();

            if (data.success) {
                // Konuşma
                let finalText = data.analysis;
                if (data.trigger_voice) {
                    finalText = data.trigger_voice + " " + finalText;
                }
                addLog("Vision: " + finalText, "azi");
                speak(finalText);
            } else {
                addLog("Vision Error: " + data.error, "sys");
                speak("Görüntü analiz edilemedi efendim.");
            }

        } catch (err) {
            console.error(err);
            addLog("Upload Error.", "sys");
        }
    };
});


// --- 2. COMMAND PROCESSING ---
async function processCommand(text) {
    try {
        addLog("Processing...", "sys");

        const res = await fetch(`${API_URL}/chat/voice`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text, client_id: 'mobile_1' })
        });

        const data = await res.json();
        const reply = data.response;

        addLog(reply, "azi");
        speak(reply);

    } catch (e) {
        addLog("Server Error: " + e.message, "sys");
    }
}

// --- 3. SPEECH SYNTHESIS (TTS) ---
function speak(text) {
    if (!window.speechSynthesis) return;

    window.speechSynthesis.cancel(); // Stop current
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'tr-TR';
    utterance.rate = 1.1; // Slightly faster

    // Find a good Turkish voice if available
    const voices = window.speechSynthesis.getVoices();
    const trVoice = voices.find(v => v.lang.includes('tr'));
    if (trVoice) utterance.voice = trVoice;

    utterance.onstart = () => {
        isSpeaking = true;
        micBtn.classList.add('speaking');
    };

    utterance.onend = () => {
        isSpeaking = false;
        micBtn.classList.remove('speaking');
    };

    window.speechSynthesis.speak(utterance);
}

// Fix for voice loading async in Chrome
window.speechSynthesis.onvoiceschanged = () => { };


// --- 4. TELEMETRY (GPS) ---
function startTracking() {
    if (!navigator.geolocation) {
        gpsCoords.innerText = "NOT SUPPORTED";
        return;
    }

    watchId = navigator.geolocation.watchPosition(
        (pos) => {
            const { latitude, longitude, accuracy, speed } = pos.coords;
            statGps.classList.remove('off');
            statGps.classList.add('on'); // Green
            gpsCoords.innerText = `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;

            // Send to Server
            sendTelemetry({
                lat: latitude,
                lon: longitude,
                acc: accuracy,
                spd: speed,
                bat: 0 // Placeholder
            });
        },
        (err) => {
            console.error("GPS Error:", err);
            statGps.classList.remove('on');
            statGps.classList.add('warn');
            gpsCoords.innerText = "NO SIGNAL";
        },
        { enableHighAccuracy: true, maximumAge: 30000, timeout: 27000 }
    );
}

async function sendTelemetry(data) {
    try {
        await fetch(`${API_URL}/telemetry/user_location`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        statServer.className = "dot"; // Green
    } catch (e) {
        statServer.className = "dot off"; // Red
    }
}


// --- UTILS ---
function addLog(text, type) {
    const div = document.createElement('div');
    div.className = `msg ${type}`;
    div.innerText = (type === 'azi' ? '> ' : '') + text;
    chatLog.prepend(div);
}

// NOTIFICATIONS
function requestNotificationPermission() {
    if ("Notification" in window) {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                console.log("Bildirim izni verildi.");
                // Test
                // new Notification("AZI Mobile", { body: "Sistem aktif." });
            }
        });
    }
}

// Sayfa acilinca veya mic basinca iste
document.addEventListener('click', () => {
    if (Notification.permission === 'default') requestNotificationPermission();
}, { once: true });

async function checkNotifications() {
    // Burada sunucudan bekleyen bildirim var mi diye sorabiliriz.
    // Simdilik demoyu basite indirgeyelim.
}

// --- 5. NEURAL LINK (WEBSOCKET) ---
let socket = null;
const WS_URL = (window.WS_BASE || API_URL.replace('http', 'ws').replace('/api', '')) + '/ws/mobile_1';

function connectNeuralLink() {
    console.log("NEURAL LINK: Bağlanıyor...", WS_URL);
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
        console.log("NEURAL LINK: ONLINE");
        statServer.className = "dot"; // Green
        addLog("Neural Link Active.", "sys");
        // Handshake
        socket.send(JSON.stringify({ type: "handshake", client: "mobile", status: "ready" }));
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);

            // 1. Proactive Voice (Server wants to speak)
            if (data.type === 'speak' || data.trigger_voice) {
                const text = data.text || data.trigger_voice;
                addLog(text, "azi");
                speak(text);
            }

            // 2. Text Response
            if (data.type === 'response') {
                addLog(data.text, "azi");
            }

            // 3. System Notification (New!)
            if (data.type === 'notification') {
                // Visual Alert
                document.body.style.backgroundColor = '#22c55e'; // Flash Green
                setTimeout(() => document.body.style.backgroundColor = '#000', 500);

                // Sound / Vibrate
                if (navigator.vibrate) navigator.vibrate([200, 100, 200]);

                // Log
                addLog(`[ALERT] ${data.title}: ${data.message}`, "sys");

                // Optional: TTS is handled by 'speak' message sent concurrently only if voice is active, 
                // but we can force it here if strictly needed. 
                // Server sends 'speak' separately, so no need to double speak.
            }

        } catch (e) {
            console.error("Socket Parse Error:", e);
        }
    };

    socket.onclose = () => {
        console.log("NEURAL LINK: OFFLINE. Retrying...");
        statServer.className = "dot off"; // Red
        setTimeout(connectNeuralLink, 3000); // Auto Reconnect
    };

    socket.onerror = (err) => {
        console.error("Socket Error:", err);
        statServer.className = "dot warn";
    };
}

// INIT
startTracking();
connectNeuralLink(); // Start WebSocket

// Keep-Alive & GPS Sync
setInterval(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
        // GPS verisini socket üzerinden de atabiliriz (daha hızlı)
        // socket.send(JSON.stringify({ type: "ping" }));
    }
}, 30000);
