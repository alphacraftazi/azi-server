import webview
import json
import os
import sys
import subprocess
import ctypes
import time
import urllib.request
import urllib.error
import threading
import platform
import socket

# Veri dosyası yolu
DATA_FILE = 'data.json'

# --- REMOTE SERVER LOGIC (AZI Entegrasyonu) ---
SERVER_URL = "http://localhost:8001" # AZI Server URL

def get_base_path():
    """Uygulamanın kalıcı veri dosyasının bulunacağı dizini belirler."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_html_path():
    """HTML dosyasinin paket icindeki yolunu belirler."""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable), 'index_stock.html')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index_stock.html')

def load_all_data():
    """Uygulama başladığında tüm verileri dosyadan yükler."""
    data_file_path = os.path.join(get_base_path(), DATA_FILE)
    
    if os.path.exists(data_file_path):
        with open(data_file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                print("Hata: data.json dosyasi bozuk veya bos. Sifirdan baslatiliyor.")
                return {}
    return {}

def save_data_to_file(data):
    """Tüm verileri tek bir dosyaya kaydeder."""
    data_file_path = os.path.join(get_base_path(), DATA_FILE)
    try:
        with open(data_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"[FATAL ERROR] Veri kaydetme hatasi: {e}")
        return False

# Tüm verileri başlangıçta yükle
APP_DATA = load_all_data()

def get_system_info():
    try:
        return {
            "pc_name": platform.node(),
            "os": f"{platform.system()} {platform.release()}",
            "processor": platform.processor(),
            "ip": socket.gethostbyname(socket.gethostname())
        }
    except:
        return {"error": "info_extract_failed"}

def handle_server_command(cmd, args):
    """Sunucudan gelen komutları işler."""
    try:
        if cmd == "popup":
            msg = args.get("msg", "Duyuru")
            title = args.get("title", "Alpha Craft System")
            ctypes.windll.user32.MessageBoxW(0, msg, title, 0x40 | 0x1) 
        elif cmd == "shutdown":
            subprocess.call(["shutdown", "/s", "/t", "10"])
        elif cmd == "lock":
            ctypes.windll.user32.LockWorkStation()
        elif cmd == "open_url":
            url = args.get("url")
            if url:
                os.system(f"start {url}")
        print(f"COMMAND EXECUTED: {cmd}")
    except Exception as e:
        print(f"Command Error: {e}")

def check_remote_license(key):
    try:
        url = f"{SERVER_URL}/api/license/check"
        sys_info = get_system_info()
        
        payload = {
            "license_key": key,
            "system_info": sys_info
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            if "command" in result:
                threading.Thread(target=handle_server_command, args=(result["command"], result.get("args", {}))).start()
            return result
    except Exception as e:
        print(f"Lisans sunucusuna ulaşılamadı: {e}")
        # Hata durumunda OFFLINE MODE olarak devam et
        # Bu sayede sunucu olmayan bilgisayarda da açılır
        return {"valid": True, "business_name": "Offline Mode", "id": 0}

def sync_data_background(key, data_type, content):
    def run():
        try:
            url = f"{SERVER_URL}/api/sync"
            payload = {
                "license_key": key,
                "data_type": data_type,
                "content": content
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=10) as response:
                print(f"[SYNC] Veri gönderildi: {data_type}")
        except Exception as e:
            print(f"[SYNC ERROR] {e}")

    threading.Thread(target=run, daemon=True).start()

class Api:
    """JavaScript ile Python arasında iletişim API'si."""
    def __init__(self, app_data, auto_license_key=None):
        self.app_data = app_data
        self.auto_license_key = auto_license_key
        
    def get_auto_license(self):
        """Varsa otomatik lisans anahtarını döndürür."""
        return self.auto_license_key
        
    def check_license(self, key):
        """Lisansı uzaktan kontrol eder."""
        return check_remote_license(key)

    def sync_telemetry(self, key, data_type, content_json):
        """Arka planda veri gönderir (UI bekletmez)."""
        try:
            content = json.loads(content_json)
            sync_data_background(key, data_type, content)
            return True
        except:
            return False

    def load_data(self, collection_name):
        """Belirtilen koleksiyonun verisini döndürür."""
        data = self.app_data.get(collection_name, [])
        if isinstance(data, (list, dict)):
            # JS Tarafındaki bozuk kayıt filtreleme için tam veri gönderiyoruz
            return json.dumps(data, ensure_ascii=False)
        return "[]"

    def save_data(self, collection_name, data_json):
        """Belirtilen koleksiyonun verisini kaydeder."""
        try:
            data = json.loads(data_json)
            self.app_data[collection_name] = data
            
            # Her kayıtta dosyaya yaz (Stable Logic)
            success = save_data_to_file(self.app_data)
            return success
            
        except json.JSONDecodeError:
            print("Hata: JavaScript'ten gelen veri JSON formatinda degil.")
            return False
        except Exception as e:
            print(f"Genel kaydetme hatasi: {e}")
            return False

def start_app():
    """Pywebview uygulamasını başlatır."""
    
    # Config dosyasından lisans anahtarı okuma (AZI özelliği)
    config_path = os.path.join(get_base_path(), "config.json")
    auto_license = None
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                auto_license = config.get("license_key")
                # URL Overwrite
                if config.get("server_url"):
                    global SERVER_URL
                    SERVER_URL = config.get("server_url")
                    print(f"Server URL Config'den yüklendi: {SERVER_URL}")
        except Exception as e:
            print(f"Config okuma hatası: {e}")

    # Fallback: license.key (Factory tarafından oluşturulan)
    if not auto_license:
        license_path = os.path.join(get_base_path(), "license.key")
        if os.path.exists(license_path):
            try:
                with open(license_path, 'r', encoding='utf-8') as f:
                    auto_license = f.read().strip()
            except Exception as e:
                print(f"License file okuma hatası: {e}")

    html_file_path = get_html_path()
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Hata: HTML dosyasi bulunamadi: {html_file_path}")
        return

    # API'yi başlatırken mevcut verileri ve lisansı veriyoruz
    api = Api(APP_DATA, auto_license_key=auto_license)
    window = webview.create_window(
        'Alpha Craft Stock Otomasyonu', 
        html=html_content, 
        js_api=api,
        width=1400, 
        height=900, 
        min_size=(900, 700),
        frameless=False
    )
    
    # Arka planda lisans kontrol döngüsü (Otomatik kontrol varsa)
    if auto_license:
        def bg_loop():
            while True:
                try:
                    check_remote_license(auto_license)
                except: pass
                time.sleep(30)
        
        threading.Thread(target=bg_loop, daemon=True).start()
    
    
    # --- TELEMETRY START ---
    try:
        import telemetry
        license_key = "DEMO_STOCK_001"
        license_path = os.path.join(get_base_path(), "license.key")
        if os.path.exists(license_path):
            with open(license_path, "r") as f: license_key = f.read().strip()
            
        t_worker = telemetry.TelemetryWorker(license_key, "AlphaStock", DATA_FILE, api)
        t_worker.start()
        print("Stock Telemetry Active.")
    except Exception as e:
        print(f"Telemetry Failed: {e}")
    # -----------------------

    webview.start()

if __name__ == '__main__':
    start_app()