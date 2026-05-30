# AZI ÖZ-BİLİNÇ VE SİSTEM HAFIZASI

Tarih: 2026-05-30 13:57

Bu belge AZI'nin kendi ekosistemini tanıması için otomatik oluşturulmuştur.

## AZI Server (azi_server/)
- **main.py**: FastAPI uygulaması. Port 8001. WebSocket (/ws), lisans API'leri, emlak, lead hunter, factory endpoint'leri barındırır.
- **database.py**: SQLite veritabanı bağlantısı (SQLAlchemy).
- **models.py**: Business, DataLog, AIMemory, CommandQueue, RealEstateListing, UserActivity, Lead, SiteRequest tabloları.
- **brain/logic.py**: AZIBrain sınıfı. Gemini 2.0-flash ile [[KOMUT]] etiket sistemini işler. Araçları tetikler.
- **brain/architect.py**: Müşteri için sıfırdan Python masaüstü uygulaması kodu üretir.
- **brain/voice.py**: Edge-TTS (tr-TR-AhmetNeural) ile Türkçe ses dosyası üretir. Cache'ler.
- **brain/proactive.py**: Pazar 03:00'de otomatik emlak scraper çalıştırır.
- **brain/notifications.py**: ntfy.sh üzerinden telefona push bildirim gönderir. Kanal: azi_core_system_alpay_v4.
- **brain/tools_web.py**: Web arama aracı.
- **brain/tools_google.py**: Gmail okuma ve takvim entegrasyonu.
- **brain/tools_smtp.py**: SMTP ile HTML mail gönderimi. Gmail App Password ile alpay.zorbek@alphacraftazi.com üzerinden gönderir.
- **brain/tools_pc.py**: Masaüstü uygulama açma, dosya listeleme.
- **brain/weather.py**: Hava durumu servisi.
- **brain/marketing.py**: Sunum içerikleri, toplu lead mail gönderimi.
- **brain/lead_hunter.py**: DuckDuckGo (ddgs) ile sektörel e-posta avcılığı. Hedef: cafe, restoran, emlak, perakende, kurumsal.
- **brain/analysis.py**: Haftalık ciro trendi, sistem sağlık skoru.
- **brain/connectors.py**: İstemci uygulamalardan gelen veri birleştirici.
- **brain/vision.py**: Kamera görüntüsü analizi. OpenCV yerel yüz tespiti + Gemini bulut analizi hibrit sistemi.
- **routers/city.py**: Şehir CRM - harita pin/not/ziyaret aktiviteleri.
- **routers/factory.py**: İstemci uygulama paketleme (PyInstaller).
- **routers/telemetry.py**: Telemetri verileri.
- **routers/vision.py**: Vision router.

## AZI Dashboard (azi_app/)
- **index.html**: Ana dashboard. AZI göz animasyonu, chat arayüzü, ses butonu. WebSocket bağlantısı.
- **blackbox.html**: Yönetim paneli (Blackbox). Lisans listesi, telemetri kartları, lead hunter, factory.
- **ac_emlak.html**: Emlak CRM paneli. Portföy yönetimi.
- **ac_stock.html**: Stok izleme paneli.
- **ac_staff.html**: Personel yönetimi paneli.
- **mobile.html**: Telefon arayüzü. GPS takibi ve sesli komut.
- **investment.html**: Yatırımcı sunumu.
- **app.js**: WebSocket yönetimi, mesaj gönderme, ses çalma, aksiyon handler.
- **blackbox.js**: Yönetim paneli JS mantığı. Lisans oluşturma, komut gönderme.
- **city_crm.js**: Harita tabanlı CRM sistemi (Leaflet.js).
- **lead_hunter.js**: Lead tarama ve sunum gönderme arayüzü.
- **vision.js**: Kamera akışı yakalama ve Gemini'ye gönderme.

## Satılan Ürünler (İstemci Uygulamaları)
- **Alpha Craft Stok** (alpha_craft_stok/main.py): PyWebview + SQLite. Lisans doğrulaması localhost:8001 üzerinden. Stok giriş/çıkış, kritik seviye uyarısı, QR kod, ciro takibi.
- **Alpha Emlak Pro** (alpha_emlak_pro/main.py): PyWebview + pandas. Portföy takibi, Excel senkronizasyonu. Veri dizini: C:\AlphaCraft_Emlak.
- **Alpha Craft Staff** (alpha_craft_staff/main_pro2.py): PyWebview. Personel, vardiya, maaş, izin takibi.
- **Alpha Craft Class** (alpha_craft_class/main_cloud_tracking.py): PyWebview. Dershane/sınıf yoklama ve takip.

## Web Sitesi (alphacraft_website/)
- Kurumsal site: alphacraftazi.com
- Sayfalar: index.html (ana), products.html (ürünler), contact.html (iletişim)

## Müşteri Sunumları (Alpha_Sunumlar_TekDosya/)
- Alpha_Genel_Musteri_Sunumu.html, Alpha_Emlak_Sunum_Mobil.html, Alpha_Staff_Sunum_Mobil.html
- Alpha_Stock_Sunum_Mobil.html, Alpha_Yatirim_Sunum_Mobil.html

## İletişim ve Kimlik Bilgileri
- Kurucu: Alpay Zorbek (Alpay Bey)
- Mail: alpay.zorbek@alphacraftazi.com
- Tel: +90 533 663 96 39
- Site: alphacraftazi.com
- Push Kanal: ntfy.sh/azi_core_system_alpay_v4

## Komut Etiketlerim ([[]] Sistemi)
- [[SEARCH: sorgu]] - Web araması
- [[GOOGLE_MAIL]] - Gmail oku
- [[SEND_MAIL: alici | konu | mesaj]] - SMTP mail gönder
- [[GOOGLE_CALENDAR]] - Takvim oku
- [[SEND_PRESENTATION: ürün | mail]] - Sunum gönder (stok/crm/staff/invest)
- [[FIND_LEADS: sektor]] - Müşteri avcısı
- [[WEATHER: şehir]] - Hava durumu
- [[OPEN_APP: uygulama]] - PC'de uygulama aç
- [[READ_FILES: klasör]] - Dosya listele
- [[OPEN_BLACKBOX]] - Yönetim panelini aç
- [[CMD: lisans|komut|args]] - İstemciye uzaktan komut
- [[ANALYSIS]] - Sistem analizi raporu
- [[LEARN: bilgi]] - Bilgiyi hafızaya kaydet
- [[PUSH_NOTIFICATION: başlık | mesaj]] - Telefona bildirim gönder
