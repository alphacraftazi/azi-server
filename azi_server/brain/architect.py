import google.generativeai as genai
import os
import time
from . import logic

class SolutionArchitect:
    def __init__(self):
        # API Key logic.py'de yuklenmisti, burada configure edilmis olmali.
        # Edilmediyse tekrar edelim.
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def generate_code(self, requirements: str, business_name: str) -> str:
        """
        Kullanıcının ihtiyaçlarına göre tek dosyalık bir Python masaüstü uygulaması yazar.
        Hata durumunda (Quota Exceeded vb.) 3 kez dener.
        """
        
        prompt = f"""
        Sen UZMAN YAZILIM MİMARI'sın.
        Görev: Aşağıdaki gereksinimlere göre, Python, PyWebview ve SQLite kullanarak, TEK DOSYALIK (stand-alone) çalışan bir GUI masaüstü yazılımı kodla.
        
        İşletme Adı: {business_name}
        Gereksinimler/Sorun: {requirements}
        
        Teknik Kurallar:
        1. Kütüphaneler: `webview` (pywebview), `sqlite3`, `json`, `datetime`.
        2. Veritabanı: Uygulama başladığında `app_data.db` adında sqlite veritabanı oluşturmalı ve gerekli tabloları kurmalı.
        3. Arayüz: HTML/CSS/JS string içinde olmalı. Modern, karanlık tema, "Cyberpunk" veya "Modern Clean" tasarımı kullan.
        4. Fonksiyonlar: Gereksinimdeki sorunu çözecek en az 2 temel özellik ekle (Örn: Sipariş ekle/listele, Personel ekle/listele).
        5. Javascript-Python iletişimi: `window.pywebview.api.call_python_func()` yapısını kullan.
        6. Çıktı SADECE Python kodu olmalı. Markdown blokları, açıklama metinleri EKLEME. Direkt kod başlasın.
        
        Önemli: Kod hatasız çalışmalı ve `if __name__ == '__main__':` bloğu ile başlamalı.
        """
        
        retries = 3
        for attempt in range(retries):
            try:
                response = self.model.generate_content(prompt)
                code = response.text
                
                # Temizlik (Markdown işaretlerini kaldır)
                if code.startswith("```python"):
                    code = code.replace("```python", "", 1)
                if code.startswith("```"):
                    code = code.replace("```", "", 1)
                if code.endswith("```"):
                    code = code.rsplit("```", 1)[0]
                    
                return code.strip()
                
            except Exception as e:
                print(f"Architect Error (Attempt {attempt+1}): {e}")
                time.sleep(2 * (attempt + 1))

        # Fallback Code if all retries fail
        return """
import webview

def create_window():
    html = \"\"\"
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body { background: #111; color: #f0f0f0; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; flex-direction: column; text-align:center; }
        h1 { color: #ff4444; }
        p { color: #888; }
        .btn { background: #333; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 20px; display:inline-block; cursor:pointer;}
    </style>
    </head>
    <body>
        <h1>SISTEM HATASI</h1>
        <p>Yazılım Mimarı şu an çok yoğun (AI Kota Sınırı).</p>
        <p>Lütfen daha sonra tekrar deneyin veya destek ile iletişime geçin.</p>
        <div class="btn" onclick="window.location.reload()">TEKRAR DENE</div>
    </body>
    </html>
    \"\"\"
    webview.create_window('HATA', html=html, width=400, height=300)
    webview.start()

if __name__ == '__main__':
    create_window()
"""

architect_service = SolutionArchitect()
