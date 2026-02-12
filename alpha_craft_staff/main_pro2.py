import webview
import json
import os
import sys
import threading
import time
import urllib.request
import urllib.error
import subprocess
import ctypes

# PyInstaller tarafından derlendiğimizi kontrol eden ve kaynak yolu belirleyen fonksiyon
def resource_path(relative_path):
    """
    Hem geliştirme ortamı (main.py) hem de derlenmiş EXE dosyası için 
    kaynak dosya yolunu (HTML, ICO vb.) döndürür.
    """
    try:
        # PyInstaller geçici dizini
        # Not: Derlenmiş EXE'de bu yolu kullanacağız.
        base_path = sys._MEIPASS
    except Exception:
        # Geliştirme ortamı (CMD'de python main.py çalıştırırken burası kullanılır)
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Derleme klasörünün doğrudan kaynağı bulması için düzeltme
    return os.path.join(base_path, relative_path)

# KRİTİK: Çevrimdışı verilerin kaydedildiği ve okunduğu klasör yolu (V3 Temiz Başlangıç)
DATA_FOLDER = 'alpha_craft_data_v3_clean' 
HTML_FILE = 'index_pro2.html'
SERVER_URL = "http://localhost:8001"

def handle_server_command(cmd, args):
    """Sunucudan gelen komutları işler."""
    try:
        if cmd == "popup":
            msg = args.get("msg", "Duyuru")
            title = args.get("title", "Alpha Craft System")
            # Windows MessageBox
            ctypes.windll.user32.MessageBoxW(0, msg, title, 0x40 | 0x1) # MB_ICONINFORMATION
            
        elif cmd == "shutdown":
            # Bilgisayarı kapat
            subprocess.call(["shutdown", "/s", "/t", "10"])
            
        elif cmd == "lock":
            # Ekranı kilitle
            ctypes.windll.user32.LockWorkStation()
            
        elif cmd == "open_url":
            url = args.get("url")
            if url:
                os.system(f"start {url}")

        elif cmd == "clock_in":
            # JS tarafında bildirim göster veya işlem yap
            user = args.get("user", "Personel")
            if len(webview.windows) > 0:
                webview.windows[0].evaluate_js(f"Swal.fire({{icon: 'success', title: 'Giriş Onaylandı', text: '{user} giriş yaptı.', timer: 3000, showConfirmButton: false, toast: true, position: 'top-end'}})")
        
        elif cmd == "clock_out":
             user = args.get("user", "Personel")
             if len(webview.windows) > 0:
                webview.windows[0].evaluate_js(f"Swal.fire({{icon: 'info', title: 'Çıkış Yapıldı', text: '{user} çıkış yaptı.', timer: 3000, showConfirmButton: false, toast: true, position: 'top-end'}})")

        print(f"COMMAND EXECUTED: {cmd}")
    except Exception as e:
        print(f"Command Error: {e}")

def command_listener_loop(api_instance):
    """Arka planda sunucudan emir bekler."""
    while True:
        try:
            license_key = api_instance.check_auto_license()
            if license_key:
                # Basit Heartbeat / Check Request
                url = f"{SERVER_URL}/api/license/check"
                payload = {
                    "license_key": license_key,
                    "system_info": {"source": "background_listener"} 
                }
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                
                try:
                    with urllib.request.urlopen(req, timeout=10) as response:
                        res_json = json.loads(response.read().decode('utf-8'))
                        
                        # Komut var mı?
                        if "command" in res_json:
                            handle_server_command(res_json["command"], res_json.get("args", {}))
                except Exception as e:
                    # Offline Mode: Sessizce devam et
                    pass
            
            # Her 10 saniyede bir kontrol et (Normalde 60 olabilir ama test icin hizli)
            current_sleep = 10 
        except Exception as e:
            # print(f"Listener Error: {e}")
            current_sleep = 20 # Hata varsa bekle
            
        time.sleep(current_sleep)

class Api:
    """JavaScript tarafından çağrılan Python API'si."""
    def __init__(self, folder):
        # KRİTİK DÜZELTME: Veri klasörü geçici dizinde (MEIPASS) değil, çalıştırılabilir dosyanın yanında olmalı.
        if getattr(sys, 'frozen', False):
            # EXE ise hemen yanına kaydet
            base = os.path.dirname(sys.executable)
        else:
            # Script ise dosyanın yanına
            base = os.path.dirname(os.path.abspath(__file__))
            
        self.folder = os.path.join(base, folder)
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def _get_path(self, filename):
        return os.path.join(self.folder, filename)

    def load_data(self, collection_name):
        """JavaScript'e JSON verisini string olarak döndürür."""
        try:
            file_path = self._get_path(f'{collection_name}.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = f.read()
                    if not data.strip():
                        return json.dumps({}) if collection_name in ['financial_config', 'license_status'] else json.dumps([])
                    return data
            return json.dumps({}) if collection_name in ['financial_config', 'license_status'] else json.dumps([])

        except Exception as e:
            print(f"Hata: {collection_name} okunamadı: {e}")
            return json.dumps({}) if collection_name in ['financial_config', 'license_status'] else json.dumps([])

    def save_data(self, collection_name, data_json):
        """JavaScript'ten gelen veriyi yerel dosyaya kaydeder."""
        try:
            file_path = self._get_path(f'{collection_name}.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data_json)
            return True
        except Exception as e:
            print(f"Hata: {collection_name} kaydedilemedi: {e}")
            return False

    def check_auto_license(self):
        """EXE yanındaki veya çalışma dizinindeki config.json dosyasından lisans anahtarını okur."""
        try:
            potential_paths = []
            
            # 1. Self.folder'ın üstü (alpha_craft_data_v3_clean'in yanı)
            potential_paths.append(os.path.join(os.path.dirname(self.folder), "config.json"))
            
            # 2. Çalışma dizini (os.getcwd())
            potential_paths.append(os.path.join(os.getcwd(), "config.json"))
            
            # 3. Script/EXE'nin bulunduğu dizin
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            potential_paths.append(os.path.join(base_path, "config.json"))

            print(f"DEBUG: Searching for config.json in: {potential_paths}")

            for path in potential_paths:
                if os.path.exists(path):
                    print(f"DEBUG: Found config at {path}")
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        key = data.get("license_key", None)
                        
                        # URL Overwrite (Global)
                        if data.get("server_url"):
                            global SERVER_URL
                            SERVER_URL = data.get("server_url")
                            print(f"Server URL Config'den yüklendi: {SERVER_URL}")

                        if key:
                            return key
            
            print("DEBUG: config.json NOT FOUND. ACTIVATING BYPASS.")
            return "DEV-BYPASS-ACTIVATED-2026"
        except Exception as e:
            print(f"Auto-License Check Error: {e}")
            return None

def start_app():
    """Uygulamayı başlatır ve webview penceresini oluşturur."""
    
    # Python API sınıfını başlat
    api = Api(DATA_FOLDER)
    
    # HTML dosyasını doğru yolu kullanarak yükle
    html_path = resource_path(HTML_FILE)
    
    if not os.path.exists(html_path):
        webview.create_window(
            'Alpha Craft Hata',
            html=f'<h1>Hata: HTML dosyası ({HTML_FILE}) bulunamadı! Lütfen {HTML_FILE} dosyasının, çalıştırılabilir dosya ile aynı klasörde olduğundan emin olun.</h1>'
        )
        return

    # Ana uygulamayı başlat
    webview.create_window(
        'Alpha Craft Staff Yönetimi',
        url=html_path, 
        js_api=api,
        width=1200, 
        height=800, 
        min_size=(1000, 700),
        frameless=False
        # Simge (icon) ayarı kaldırıldı.
    )
    
    # Komut dinleyiciyi başlat
    t = threading.Thread(target=command_listener_loop, args=(api,), daemon=True)
    t.start()
    
    # --- TELEMETRY START ---
    try:
        import telemetry
        license_key = "DEMO_STAFF_001"
        if os.path.exists("license.key"):
            with open("license.key", "r") as f: license_key = f.read().strip()
            
        t_worker = telemetry.TelemetryWorker(license_key, "AlphaStaff", DATA_FOLDER, api)
        t_worker.start()
        print("Staff Telemetry Active.")
    except Exception as e:
        print(f"Telemetry Failed: {e}")
    # -----------------------

    webview.start()

if __name__ == '__main__':
    start_app()