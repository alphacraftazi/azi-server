# azi_server/brain/tools_definitions.py
from typing import Optional

def search_web(query: str) -> str:
    """İnternette (Web'de) güncel bilgi araması yapar. Kullanıcının sormuş olduğu güncel bilgiler, döviz kurları, şirketler veya genel araştırma konuları için kullanılır.
    Args:
        query: İnternette aranacak kelime öbeği veya soru.
    """
    from azi_server.brain import tools_web
    return tools_web.search_web(query)

def get_weather(city: str) -> str:
    """Belirtilen şehrin güncel hava durumunu getirir.
    Args:
        city: Hava durumu öğrenilecek şehrin adı (Örn: 'Istanbul', 'Ankara').
    """
    from azi_server.brain.weather import weather_service
    return weather_service.get_weather(city)

def get_unread_emails() -> str:
    """Kullanıcının Google (Gmail) gelen kutusundaki okunmamış e-postaları kontrol eder ve listeler."""
    from azi_server.brain import tools_google
    return tools_google.get_unread_emails()

def get_calendar_events() -> str:
    """Kullanıcının Google Takvimindeki (Calendar) yaklaşan etkinliklerini ve toplantılarını okur."""
    from azi_server.brain import tools_google
    return tools_google.get_calendar_events()

def get_system_status() -> str:
    """Kullanıcının GÜNCEL FİZİKSEL BİLGİSAYARININ (CPU, RAM, Disk) durumunu Ajan üzerinden okumak için komut gönderir. Bilgisayarın kasıp kasmadığı buradan anlaşılır."""
    return "COMMAND_QUEUED_FOR_AGENT"

def run_system_command_terminal(command: str) -> str:
    """Kullanıcının fiziksel bilgisayarındaki CMD/Powershell (Terminal) üzerinden sistem komutu çalıştırır. (Örn: Dosya bulma, ağ kontrolü, klasör listeleme, script başlatma).
    Args:
         command: Windows CMD veya Powershell'de çalıştırılacak sistem komutu (Örn: 'dir %USERPROFILE%\\Desktop').
    """
    return "COMMAND_QUEUED_FOR_AGENT"

def kill_process(process_name: str) -> str:
    """Kullanıcının bilgisayarında arka planda çalışan veya kilitlenen bir uygulamayı/işlemi zorla (force kill) sonlandırır. (Örn: chrome'u kapat).
    Args:
        process_name: Sonlandırılacak işlemin exesinin adı (Örn: 'chrome.exe', 'notepad.exe').
    """
    return "COMMAND_QUEUED_FOR_AGENT"

def open_application(app_name: str) -> str:
    """Kullanıcının bilgisayarında bir uygulama, modül veya bir web sitesi (Spotify, Youtube vb.) açar.
    Args:
        app_name: Açılacak uygulamanın, web sitesinin veya Alpha modülünün adı (Örn: 'Spotify', 'Youtube', 'Emlak').
    """
    return "COMMAND_QUEUED_FOR_AGENT"

def send_email_smtp(to_email: str, subject: str, message: str) -> str:
    """Birisine e-posta (mail) göndermek için kullanılır.
    Args:
        to_email: Mailin gönderileceği alıcı adresi.
        subject: Mailin kısa konusu.
        message: Mailin içeriği (Uzun metin).
    """
    from azi_server.brain import tools_smtp
    return tools_smtp.send_email_smtp(to_email, subject, message, attachment_paths=[])

def find_customer_leads(sector: str) -> str:
    """İnternetten belirtilen sektör için potansiyel müşteri e-postaları toplar (Müşteri Avcısı). (Örn: Restoran, Kafe, Emlak).
    Args:
        sector: Hedef sektör (Örn: 'restoran', 'kafe', 'emlak', 'kurumsal').
    """
    return f"Leads search initiated for {sector}. Lütfen kullanıcıya aramaya başladığınızı bildirin. Veri büyüklüğü nedeniyle asenkron çalışacaktır."

def generate_system_analysis_report() -> str:
    """Şirketin genel durumunu, stok, emlak, personel ve sistem gelirlerini özetleyen detaylı bir analiz (ciro) raporu çıkarır."""
    try:
        from azi_server.brain import analysis
        from azi_server import database
        db = database.SessionLocal()
        report = analysis.analysis_service.generate_brief_for_azi(db)
        db.close()
        return report
    except Exception as e:
        return f"Rapor okunamadı: {e}"

def push_notification_to_mobile(title: str, message: str) -> str:
    """Kullanıcının (Alpay Bey'in) cep telefonuna anlık PUSH Bildirim (Alert) veya rapor gönderir. Kullanıcı 'Bana bildir', 'Cebime gönder' derse kesinlikle kullanılmalıdır.
    Args:
        title: Bildirimin kısa başlığı.
        message: Bildirimin tam metni veya raporun içeriği.
    """
    try:
        from azi_server.brain.notifications import notifier
        import asyncio
        import nest_asyncio
        nest_asyncio.apply() # To allow nested event loops just in case
        
        loop = asyncio.get_event_loop()
        loop.create_task(notifier.send_async(title, message, priority=3))
        return "Bildirim başarıyla gönderildi."
    except Exception as e:
        return f"Bildirim gönderilemedi: {e}"

def list_directory(path: str) -> str:
    """Kullanıcının bilgisayarındaki bir klasörün içindeki dosyaları ve alt klasörleri listeler.
    Args:
        path: Görüntülenecek klasörün tam adresi (Örn: 'C:\\Users\\alpay\\Desktop' veya sadece '.' mevcut dizin için).
    """
    return "COMMAND_QUEUED_FOR_AGENT"

def view_file(path: str) -> str:
    """Kullanıcının bilgisayarındaki bir metin/kod dosyasının tüm içeriğini okur ve AZI'ye getirir.
    Args:
        path: Okunacak dosyanın tam adresi (Örn: 'main.py' veya 'C:\\test.txt').
    """
    return "COMMAND_QUEUED_FOR_AGENT"

def write_to_file(path: str, content: str) -> str:
    """Kullanıcının bilgisayarında yeni bir dosya oluşturur veya var olan kod dosyasını tamamen yenisiyle değiştirir (Kod yazma/düzenleme).
    Args:
        path: Yazılacak dosyanın tam adresi.
        content: Dosyaya yazılacak olan tamamlanmış kodlar veya metin (eksiksiz olmalıdır).
    """
    return "COMMAND_QUEUED_FOR_AGENT"

def search_past_memory(keyword: str) -> str:
    """Geçmişteki eski konuşmaları, hafızayı veya eski verileri hatırlamak/bulmak için AZI'nin veritabanında derinlemesine arama yapar (Uzun Süreli Hafıza - RAG).
    Args:
        keyword: Veritabanında (eski tarihlerde) aranacak anahtar kelime veya içerik.
    """
    try:
        from azi_server import database, models
        db = database.SessionLocal()
        results = db.query(models.AIMemory).filter(models.AIMemory.content.ilike(f"%{keyword}%")).order_by(models.AIMemory.id.desc()).limit(15).all()
        db.close()
        
        if not results: return "Bu konuyla ilgili geçmiş hafızamda hiçbir kayıt bulamadım."
        
        memories = []
        for r in results:
            role = "AZI" if r.memory_type == "azi_response" else "Kullanıcı"
            time_str = r.timestamp.strftime("%Y-%m-%d %H:%M") if r.timestamp else "Geçmiş"
            memories.append(f"[{time_str}] {role}: {r.content[:300]}...")
        return "Geçmiş Hafıza Kayıtları:\n" + "\n---\n".join(memories)
    except Exception as e:
        return f"Hafıza erişim hatası: {e}"

def browse_website_via_agent(url: str) -> str:
    """Kullanıcının bilgisayarındaki Ajan (Sinir Ucu) üzerinden bir web sitesine gizlice bağlanır, sayfa kodlarını okur ve metinleri kazıyıp getirir (Web Scraping / Tarayıcı Botu). Link verilirse mutlaka kullanılır.
    Args:
        url: Taranacak web sitesinin tam linki (https://...).
    """
    return "COMMAND_QUEUED_FOR_AGENT"

# Tüm agentik araçların listesi
azi_tool_list = [
    search_web, get_weather, get_unread_emails, get_calendar_events,
    get_system_status, run_system_command_terminal, kill_process,
    open_application, send_email_smtp, find_customer_leads,
    generate_system_analysis_report, push_notification_to_mobile,
    list_directory, view_file, write_to_file,
    search_past_memory, browse_website_via_agent
]
