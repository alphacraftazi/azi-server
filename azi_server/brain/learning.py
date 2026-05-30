import os
import datetime

class SelfLearner:
    """
    Azi'nin kendi kod tabanını ve yeteneklerini öğrenmesini sağlayan modül.
    """

    def __init__(self, root_dir=None):
        if not root_dir:
            self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        else:
            self.root_dir = root_dir

        self.knowledge_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "azi_knowledge.md")

    def _read_head(self, file_path, lines=5):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return " | ".join(f.readline().strip() for _ in range(lines) if True)
        except:
            return ""

    def scan_codebase(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        summary = f"# AZI ÖZ-BİLİNÇ VE SİSTEM HAFIZASI\n\nTarih: {now}\n\n"
        summary += "Bu belge AZI'nin kendi ekosistemini tanıması için otomatik oluşturulmuştur.\n\n"

        # --- SUNUCU ---
        summary += "## AZI Server (azi_server/)\n"
        summary += "- **main.py**: FastAPI uygulaması. Port 8001. WebSocket (/ws), lisans API'leri, emlak, lead hunter, factory endpoint'leri barındırır.\n"
        summary += "- **database.py**: SQLite veritabanı bağlantısı (SQLAlchemy).\n"
        summary += "- **models.py**: Business, DataLog, AIMemory, CommandQueue, RealEstateListing, UserActivity, Lead, SiteRequest tabloları.\n"
        summary += "- **brain/logic.py**: AZIBrain sınıfı. Gemini 2.0-flash ile [[KOMUT]] etiket sistemini işler. Araçları tetikler.\n"
        summary += "- **brain/architect.py**: Müşteri için sıfırdan Python masaüstü uygulaması kodu üretir.\n"
        summary += "- **brain/voice.py**: Edge-TTS (tr-TR-AhmetNeural) ile Türkçe ses dosyası üretir. Cache'ler.\n"
        summary += "- **brain/proactive.py**: Pazar 03:00'de otomatik emlak scraper çalıştırır.\n"
        summary += "- **brain/notifications.py**: ntfy.sh üzerinden telefona push bildirim gönderir. Kanal: azi_core_system_alpay_v4.\n"
        summary += "- **brain/tools_web.py**: Web arama aracı.\n"
        summary += "- **brain/tools_google.py**: Gmail okuma ve takvim entegrasyonu.\n"
        summary += "- **brain/tools_smtp.py**: SMTP ile HTML mail gönderimi. Gmail App Password ile alpay.zorbek@alphacraftazi.com üzerinden gönderir.\n"
        summary += "- **brain/tools_pc.py**: Masaüstü uygulama açma, dosya listeleme.\n"
        summary += "- **brain/weather.py**: Hava durumu servisi.\n"
        summary += "- **brain/marketing.py**: Sunum içerikleri, toplu lead mail gönderimi.\n"
        summary += "- **brain/lead_hunter.py**: DuckDuckGo (ddgs) ile sektörel e-posta avcılığı. Hedef: cafe, restoran, emlak, perakende, kurumsal.\n"
        summary += "- **brain/analysis.py**: Haftalık ciro trendi, sistem sağlık skoru.\n"
        summary += "- **brain/connectors.py**: İstemci uygulamalardan gelen veri birleştirici.\n"
        summary += "- **brain/vision.py**: Kamera görüntüsü analizi. OpenCV yerel yüz tespiti + Gemini bulut analizi hibrit sistemi.\n"
        summary += "- **routers/city.py**: Şehir CRM - harita pin/not/ziyaret aktiviteleri.\n"
        summary += "- **routers/factory.py**: İstemci uygulama paketleme (PyInstaller).\n"
        summary += "- **routers/telemetry.py**: Telemetri verileri.\n"
        summary += "- **routers/vision.py**: Vision router.\n\n"

        # --- FRONTEND ---
        summary += "## AZI Dashboard (azi_app/)\n"
        summary += "- **index.html**: Ana dashboard. AZI göz animasyonu, chat arayüzü, ses butonu. WebSocket bağlantısı.\n"
        summary += "- **blackbox.html**: Yönetim paneli (Blackbox). Lisans listesi, telemetri kartları, lead hunter, factory.\n"
        summary += "- **ac_emlak.html**: Emlak CRM paneli. Portföy yönetimi.\n"
        summary += "- **ac_stock.html**: Stok izleme paneli.\n"
        summary += "- **ac_staff.html**: Personel yönetimi paneli.\n"
        summary += "- **mobile.html**: Telefon arayüzü. GPS takibi ve sesli komut.\n"
        summary += "- **investment.html**: Yatırımcı sunumu.\n"
        summary += "- **app.js**: WebSocket yönetimi, mesaj gönderme, ses çalma, aksiyon handler.\n"
        summary += "- **blackbox.js**: Yönetim paneli JS mantığı. Lisans oluşturma, komut gönderme.\n"
        summary += "- **city_crm.js**: Harita tabanlı CRM sistemi (Leaflet.js).\n"
        summary += "- **lead_hunter.js**: Lead tarama ve sunum gönderme arayüzü.\n"
        summary += "- **vision.js**: Kamera akışı yakalama ve Gemini'ye gönderme.\n\n"

        # --- ÜRÜNLER ---
        summary += "## Satılan Ürünler (İstemci Uygulamaları)\n"
        summary += "- **Alpha Craft Stok** (alpha_craft_stok/main.py): PyWebview + SQLite. Lisans doğrulaması localhost:8001 üzerinden. Stok giriş/çıkış, kritik seviye uyarısı, QR kod, ciro takibi.\n"
        summary += "- **Alpha Emlak Pro** (alpha_emlak_pro/main.py): PyWebview + pandas. Portföy takibi, Excel senkronizasyonu. Veri dizini: C:\\AlphaCraft_Emlak.\n"
        summary += "- **Alpha Craft Staff** (alpha_craft_staff/main_pro2.py): PyWebview. Personel, vardiya, maaş, izin takibi.\n"
        summary += "- **Alpha Craft Class** (alpha_craft_class/main_cloud_tracking.py): PyWebview. Dershane/sınıf yoklama ve takip.\n\n"

        # --- WEB SİTESİ ---
        summary += "## Web Sitesi (alphacraft_website/)\n"
        summary += "- Kurumsal site: alphacraftazi.com\n"
        summary += "- Sayfalar: index.html (ana), products.html (ürünler), contact.html (iletişim)\n\n"

        # --- SUNUMLAR ---
        summary += "## Müşteri Sunumları (Alpha_Sunumlar_TekDosya/)\n"
        summary += "- Alpha_Genel_Musteri_Sunumu.html, Alpha_Emlak_Sunum_Mobil.html, Alpha_Staff_Sunum_Mobil.html\n"
        summary += "- Alpha_Stock_Sunum_Mobil.html, Alpha_Yatirim_Sunum_Mobil.html\n\n"

        # --- İLETİŞİM ---
        summary += "## İletişim ve Kimlik Bilgileri\n"
        summary += "- Kurucu: Alpay Zorbek (Alpay Bey)\n"
        summary += "- Mail: alpay.zorbek@alphacraftazi.com\n"
        summary += "- Tel: +90 533 663 96 39\n"
        summary += "- Site: alphacraftazi.com\n"
        summary += "- Push Kanal: ntfy.sh/azi_core_system_alpay_v4\n\n"

        # --- KOMUTLarım ---
        summary += "## Komut Etiketlerim ([[]] Sistemi)\n"
        summary += "- [[SEARCH: sorgu]] - Web araması\n"
        summary += "- [[GOOGLE_MAIL]] - Gmail oku\n"
        summary += "- [[SEND_MAIL: alici | konu | mesaj]] - SMTP mail gönder\n"
        summary += "- [[GOOGLE_CALENDAR]] - Takvim oku\n"
        summary += "- [[SEND_PRESENTATION: ürün | mail]] - Sunum gönder (stok/crm/staff/invest)\n"
        summary += "- [[FIND_LEADS: sektor]] - Müşteri avcısı\n"
        summary += "- [[WEATHER: şehir]] - Hava durumu\n"
        summary += "- [[OPEN_APP: uygulama]] - PC'de uygulama aç\n"
        summary += "- [[READ_FILES: klasör]] - Dosya listele\n"
        summary += "- [[OPEN_BLACKBOX]] - Yönetim panelini aç\n"
        summary += "- [[CMD: lisans|komut|args]] - İstemciye uzaktan komut\n"
        summary += "- [[ANALYSIS]] - Sistem analizi raporu\n"
        summary += "- [[LEARN: bilgi]] - Bilgiyi hafızaya kaydet\n"
        summary += "- [[PUSH_NOTIFICATION: başlık | mesaj]] - Telefona bildirim gönder\n"

        return summary

    def learn(self):
        knowledge = self.scan_codebase()
        with open(self.knowledge_file, "w", encoding="utf-8") as f:
            f.write(knowledge)
        return "Öz-bilinç güncellendi."


learner = SelfLearner()
