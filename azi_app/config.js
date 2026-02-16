// AZI Frontend Configuration
console.log("AZI CONFIG LOADING...");

const AZI_CONFIG = {
    // PROD_URL: Canlı Sunucu Adresi (Render)
    // Burayı Render deploy sonrası size verilen adresle (örn: https://azi-brain-xyz.onrender.com) değiştirin.
    // Şimdilik domain stratejimize göre 'beyin.alphacraftazi.com' olarak bırakıyoruz.
    PROD_URL: "https://azi-server.onrender.com",

    // Port: Yerel çalışırken kullanılan port
    LOCAL_PORT: 8001,

    // Otomatik API Adresi Seçici
    getApiBase: function () {
        const host = window.location.hostname;

        // 1. Yerel Geliştirme (Localhost)
        if (host === "localhost" || host === "127.0.0.1") {
            const protocol = window.location.protocol;
            // Eğer backend ve frontend aynı porttaysa (Python serve ediyorsa)
            // Yoksa varsayılan 8001'e dön
            return `${protocol}//${host}:${this.LOCAL_PORT}`;
        }

        // 2. LAN (Wi-Fi) Erişimi (192.168.x.x veya 10.x.x.x)
        if (host.startsWith("192.") || host.startsWith("10.") || host.endsWith(".ngrok-free.app")) {
            const protocol = window.location.protocol;
            return `${protocol}//${host}:${window.location.port || this.LOCAL_PORT}`;
        }

        // 3. Canlı Ortam (Render/Cloud)
        return this.PROD_URL;

        // Eski: return window.location.origin;
    }
};

// Global Değişkenler (Tüm scriptler buradan okuyacak)
window.API_BASE = AZI_CONFIG.getApiBase();
// WebSocket adresi (http -> ws, https -> wss)
window.WS_BASE = window.API_BASE.replace("http", "ws");

console.log("AZI API TARGET:", window.API_BASE);
