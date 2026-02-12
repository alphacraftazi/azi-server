import os
import subprocess
import platform
import glob
from pathlib import Path

def get_user_folder(folder_name):
    """Kullanıcının özel klasörlerini bulur (Desktop, Documents vb.)"""
    return os.path.join(os.environ['USERPROFILE'], folder_name)

def list_user_files(location: str):
    """
    Belirtilen konumdaki dosyaları listeler.
    location: desktop, documents, downloads, pictures
    """
    location = location.lower()
    target_path = ""
    
    if "masa" in location or "desktop" in location:
        target_path = get_user_folder("Desktop")
    elif "belge" in location or "documents" in location:
        target_path = get_user_folder("Documents")
    elif "indir" in location or "download" in location:
        target_path = get_user_folder("Downloads")
    elif "resim" in location or "foto" in location or "galeri" in location or "picture" in location:
        target_path = get_user_folder("Pictures")
    else:
        return "Bilinmeyen klasör. Sadece Masaüstü, Belgeler, İndirilenler ve Resimler destekleniyor."
        
    try:
        # Son degistirilen 20 dosyayi getir
        files =  sorted(Path(target_path).iterdir(), key=os.path.getmtime, reverse=True)[:20]
        file_list = [f.name for f in files if f.is_file()]
        return f"{target_path} konumundaki son dosyalar:\n" + "\n".join(file_list)
    except Exception as e:
        return f"Dosya listeleme hatası: {str(e)}"

import webbrowser

def open_application(app_name: str):
    """
    Uygulamayı akıllıca arar ve açar. Web sitelerini de destekler.
    """
    app_name = app_name.lower().strip()
    
    # 1. Web Siteleri Kontrolü (Hızlı Erişim)
    websites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "netflix": "https://www.netflix.com",
        "twitter": "https://twitter.com",
        "instagram": "https://www.instagram.com",
        "facebook": "https://www.facebook.com",
        "whatsapp": "https://web.whatsapp.com",
        "linkedin": "https://www.linkedin.com",
        "haberler": "https://news.google.com"
    }
    
    # Doğrudan eşleşme veya "youtube aç" gibi komutlar için kontrol
    for site, url in websites.items():
        if site in app_name:
            webbrowser.open(url)
            return f"{site.capitalize()} tarayıcıda açılıyor..."

    # 1.5 PROJE UYGULAMALARI (Alpha Craft Özel)
    # Kullanıcı "emlak aç", "stok aç", "pro2" dediğinde buraya düşer.
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) 
    # tools_pc.py -> brain -> azi_server -> scratch
    
    app_mappings = {
        "emlak": os.path.join(project_root, "alpha_emlak_pro", "main.py"), # veya city_crm.py
        "stok": os.path.join(project_root, "alpha_craft_stok", "main.py"),
        "staff": os.path.join(project_root, "AlphaCraftPro2", "main_pro2.py"),
        "personel": os.path.join(project_root, "AlphaCraftPro2", "main_pro2.py"),
        "class": os.path.join(project_root, "alpha_craft_class", "main_cloud_tracking.py"),
        "dershane": os.path.join(project_root, "alpha_craft_class", "main_cloud_tracking.py")
    }
    
    for key, path in app_mappings.items():
        if key in app_name:
            if os.path.exists(path):
                try:
                    # Yeni bir terminalde python ile çalıştır
                    subprocess.Popen(f'start cmd /k python "{path}"', shell=True)
                    return f"Alpha {key.upper()} modülü başlatılıyor..."
                except Exception as e:
                    return f"Modül bulundu ama açılamadı: {e}"


    # 2. Kısayol Taraması (Start Menu & Desktop)
    search_paths = [
        os.path.join(os.environ['ProgramData'], r'Microsoft\Windows\Start Menu\Programs'),
        os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs'),
        get_user_folder("Desktop")
    ]
    
    found_lnk = None
    
    # Tam eşleşme veya içerme araması
    for path in search_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".lnk") and app_name in file.lower():
                    found_lnk = os.path.join(root, file)
                    break
            if found_lnk: break
        if found_lnk: break
        
    if found_lnk:
        try:
            os.startfile(found_lnk)
            return f"Uygulama bulundu ve başlatılıyor: {found_lnk}"
        except Exception as e:
            return f"Kısayol bulundu ama açılamadı: {e}"

    # 3. Sistem komutu olarak dene (calc, notepad vb.)
    try:
        subprocess.Popen(app_name, shell=True)
        return f"Komut olarak çalıştırıldı: {app_name}"
    except:
        # 4. Hiçbiri değilse Google'da Ara (Fallback)
        # Kullanıcı "X nedir?" veya bilinmeyen bir şey dediyse tarayıcıda arayalım.
        search_url = f"https://www.google.com/search?q={app_name}"
        webbrowser.open(search_url)
        return f"'{app_name}' bilgisayarda bulunamadı, Google'da aranıyor..."

