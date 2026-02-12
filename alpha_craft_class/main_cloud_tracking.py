import webview
import os
import sys
import json

# Bulut Tabanlı HTML Dosyasının Adı
HTML_FILE = 'index_class_tracking.html'
DATA_DIR = 'data'
SERVER_URL = "http://localhost:8001"

# CONFIG LOADING (Global)
try:
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    config_path = os.path.join(base_path, "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            cdata = json.load(f)
            if cdata.get("server_url"):
                SERVER_URL = cdata.get("server_url")
                print(f"Server URL Config'den: {SERVER_URL}")
except Exception as e:
    print(f"Config Load Error: {e}")

class Api:
    def __init__(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def save_data(self, collection, data):
        """Frontend'den gelen veriyi JSON olarak kaydeder."""
        try:
            file_path = os.path.join(DATA_DIR, f"{collection}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_server_url(self):
        """Frontend'in sunucu adresini almasını sağlar."""
        return SERVER_URL

    def load_data(self, collection):
        """İstenen koleksiyonu JSON dosyasından okur."""
        try:
            file_path = os.path.join(DATA_DIR, f"{collection}.json")
            if not os.path.exists(file_path):
                return "[]"
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return "[]"

def get_html_path():
    """Programın dosya yolunu bulur."""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable), HTML_FILE)
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), HTML_FILE)

def start_app():
    html_path = get_html_path()
    api = Api() # API Nesnesini Oluştur
    
    if not os.path.exists(html_path):
        print(f"Hata: {HTML_FILE} bulunamadı! Lütfen HTML dosyasını Python dosyasıyla aynı klasöre koyun.")
        return

    # Uygulamayı başlat
    window = webview.create_window(
        'Alpha Craft Class - Eğitim Yönetim Sistemi', 
        url=html_path, 
        width=1400, 
        height=900,
        min_size=(1000, 700),
        background_color='#020617',
        confirm_close=True,
        js_api=api # API'yi Pencereye Bağla (KRİTİK ADIM)
    )
    
    # --- TELEMETRY START ---
    try:
        # Factory build sırasında 'telemetry.py' buraya kopyalanmış olacak.
        import telemetry
        # Lisans anahtarı normalde 'license.key' dosyasından okunur.
        # Şimdilik DEMO_CLASS_001 kullanıyoruz.
        license_key = "DEMO_CLASS_001"
        if os.path.exists("license.key"):
            with open("license.key", "r") as f: license_key = f.read().strip()
            
        # Pass Global SERVER_URL (loaded from config.json) to Telemetry
        t_worker = telemetry.TelemetryWorker(license_key, "AlphaClass", DATA_DIR, api, SERVER_URL)
        t_worker.start()
        print("Müşteri Telemetri Servisi Başlatıldı.")
    except ImportError:
        print("UYARI: Telemetri modülü bulunamadı (Dev ortamı olabilir).")
    except Exception as e:
        print(f"Telemetri Hatası: {e}")
    # -----------------------

    webview.start(debug=False)

if __name__ == '__main__':
    try:
        start_app()
    except Exception as e:
        import traceback
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
            f.write("\n" + str(e))
        print("CRITICAL ERROR:", e)
        input("Press Enter to close...") # Keep window open to see error