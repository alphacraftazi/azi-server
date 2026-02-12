import webview
import json
import os
import sys

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

# KRİTİK: Çevrimdışı verilerin kaydedildiği ve okunduğu klasör yolu
DATA_FOLDER = 'alpha_craft_data' 
HTML_FILE = 'index_pro2.html'

class Api:
    """JavaScript tarafından çağrılan Python API'si."""
    def __init__(self, folder):
        # KRİTİK DÜZELTME: Veri klasörü yolunu kaynak yola bağla
        self.folder = resource_path(folder) 
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
    
    webview.start()

if __name__ == '__main__':
    start_app()