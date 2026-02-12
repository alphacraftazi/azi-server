import shutil
import json
import os
import threading
import time
from . import architect

class BuildFactory:
    """
    Universal Build Factory for Connected Ecosystem.
    Injects Telemetry and License Keys into Client Products.
    """
    def __init__(self):
        self.installers_path = os.path.join(os.getcwd(), "azi_server", "installers")
        os.makedirs(self.installers_path, exist_ok=True)
        
    def package_client(self, license_key, product_type="stock", custom_requirements=None, business_name="My Business"):
        """
        Universal Factory Builder:
        1. Identifies Product Source.
        2. Creates Temp Build Env.
        3. Injects 'telemetry.py' & 'license.key'.
        4. Zips and Returns.
        """
        try:
            # 1. Kaynak ve Hedef Belirle
            source_map = {
                "stock": "alpha_craft_stok",
                "stok": "alpha_craft_stok",
                "stok takibi": "alpha_craft_stok",
                "emlak": "alpha_emlak_pro",
                "emlak_pro": "alpha_emlak_pro",
                "emlak otomasyonu": "alpha_emlak_pro",
                "gayrimenkul": "alpha_emlak_pro",
                "crm": "alpha_emlak_pro",
                "city": "alpha_emlak_pro",
                "city crm": "alpha_emlak_pro",
                "staff": "alpha_craft_staff",
                "personel": "alpha_craft_staff",
                "personnel": "alpha_craft_staff",
                "class": "alpha_craft_class",
                "class_tracking": "alpha_craft_class"
            }
            
            target_folder = source_map.get(product_type)
            
            if not target_folder:
                 return {"success": False, "error": f"Geçersiz Ürün Tipi: '{product_type}'. (Desteklenenler: {list(source_map.keys())})"}
            
            # Locate Source Path (Handle both ./ and ../ cases)
            current_dir = os.getcwd()
            source_path = os.path.abspath(os.path.join(current_dir, target_folder))
            if not os.path.exists(source_path):
                # Try sibling directory
                source_path = os.path.abspath(os.path.join(current_dir, "..", target_folder))
            
            if not os.path.exists(source_path):
                # Try direct subdirectory
                source_path = os.path.join(current_dir, target_folder)

            if not os.path.exists(source_path):
                return {"success": False, "error": f"Kaynak Bulunamadı: {target_folder} ({source_path})"}
            
            print(f"DEBUG: Resolved Source Path: {source_path}")

            # 2. Temp Alanı Hazırla
            temp_dir = os.path.join(self.installers_path, f"Setup_{product_type.upper()}_{license_key}")
            if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)
            
            # Build Root (Zip icindeki ana klasor)
            app_dir = os.path.join(temp_dir, f"Alpha{product_type.capitalize()}")
            os.makedirs(app_dir, exist_ok=True)

            # 3. Dosyaları Kopyala (Gereksizleri Ele)
            ignore_pattern = shutil.ignore_patterns('__pycache__', 'dist', 'build', '.git', '*.spec', 'venv', '.vscode')
            
            # Copytree fails if dest exists, so we copy items individually or copy to 'App' subdir
            # Cleaning destination logic is handled above by checking temp_dir
            shutil.copytree(source_path, app_dir, ignore=ignore_pattern, dirs_exist_ok=True)

            # 3.5. Dosya İsmi Standardizasyonu (main_pro2.py -> main.py)
            # PyInstaller main.py bekliyor. Projelerde farklı isimler olabiliyor.
            current_main = os.path.join(app_dir, "main.py")
            if not os.path.exists(current_main):
                alternatives = ["main_pro2.py", "main_stock.py", "app.py", "main_cloud_tracking.py"]
                for alt in alternatives:
                    alt_path = os.path.join(app_dir, alt)
                    if os.path.exists(alt_path):
                        print(f"[{product_type}] Standardizasyon: {alt} -> main.py")
                        shutil.move(alt_path, current_main)
                        break

            # 4. TELEMETRY & LICENSE ENJEKSİYONU
            # A. Telemetry Modülünü Kopyala
            telemetry_src = os.path.join(current_dir, "azi_server", "factory_resources", "telemetry.py")
            if os.path.exists(telemetry_src):
                shutil.copy2(telemetry_src, os.path.join(app_dir, "telemetry.py"))
            else:
                print("UYARI: Main Telemetry File Found Not Found!")
            
            # B. Lisans Anahtarını Yaz
            license_path = os.path.join(app_dir, "license.key")
            with open(license_path, 'w', encoding='utf-8') as f:
                f.write(license_key)

            # ---------------------------------------------------------
            # 5. OTOMATİK DERLEME (PYINSTALLER)
            # ---------------------------------------------------------
            # Kütüphane sorununu çözmek için EXE oluşturuyoruz.
            print(f"[{product_type}] Derleme Başlatılıyor...")
            
            import subprocess
            
            # HTML dosyası varsa ekle (Stock için index_stock.html, Emlak için index.html)
            add_data_arg = []
            if product_type in ["stock", "stok", "stok takibi"]:
                if os.path.exists(os.path.join(app_dir, "index_stock.html")):
                    add_data_arg = ["--add-data", "index_stock.html;."]
            elif product_type in ["emlak", "crm", "emlak_pro"]:
                if os.path.exists(os.path.join(app_dir, "index.html")):
                    add_data_arg = ["--add-data", "index.html;."]
            elif product_type in ["staff", "personel", "personnel"]:
                if os.path.exists(os.path.join(app_dir, "index_pro2.html")):
                    add_data_arg = ["--add-data", "index_pro2.html;."]
            elif product_type in ["class", "sinif", "okul", "class_tracking"]:
                if os.path.exists(os.path.join(app_dir, "index_class_tracking.html")):
                    add_data_arg = ["--add-data", "index_class_tracking.html;."]
            
            # Icon varsa ekle (Opsiyonel - şimdilik geçiyoruz)
            
            # Use module execution to avoid PATH issues
            cmd = [
                "python", "-m", "PyInstaller",
                "--onefile",
                "--windowed",
                "--name", f"Alpha{product_type.capitalize()}",
                "--distpath", os.path.join(app_dir, "dist"),
                "--workpath", os.path.join(app_dir, "build"),
                "--specpath", app_dir,
            ] + add_data_arg + [os.path.join(app_dir, "main.py")]
            
            # Debug info
            print(f"Executing: {' '.join(cmd)}")
            
            process = subprocess.run(cmd, cwd=app_dir, capture_output=True, text=True)
            
            if process.returncode != 0:
                print(f"DERLEME HATASI:\n{process.stderr}")
                return {"success": False, "error": f"Derleme Başarısız: {process.stderr[:200]}"}
            
            print(f"[{product_type}] Derleme Başarılı!")

            # ---------------------------------------------------------
            # ---------------------------------------------------------
            # DETECT PUBLIC URL (NGROK / LAN)
            # ---------------------------------------------------------
            import builtins
            server_url = getattr(builtins, "AZI_PUBLIC_URL", None)
            
            if not server_url:
                # Fallback to LAN if not ready
                import socket
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    server_url = f"http://{s.getsockname()[0]}:8001"
                    s.close()
                except:
                    server_url = "http://localhost:8001"
            
            print(f"[{product_type}] Server URL ayarlanıyor: {server_url}")
            
            # config.json oluştur (Hem lisans hem URL için)
            config_data = {
                "license_key": license_key,
                "server_url": server_url,
                "created_at": time.time()
            }
            
            # Fix: Define dist_folder explicitly
            dist_folder = os.path.join(app_dir, "dist")
            os.makedirs(dist_folder, exist_ok=True) # Ensure it exists
            
            with open(os.path.join(dist_folder, "config.json"), 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
                
            # License key dosyası da dursun (Yedek)
            shutil.copy2(license_path, os.path.join(dist_folder, "license.key"))
            
            # 6. EKSTRA DOSYALAR (Excel vb.)
            # Emlak ve Stok programları için Excel dosyalarını yanına koyuyoruz.
            # 6. EKSTRA DOSYALAR (Excel vb.)
            # Emlak ve Stok programları için Excel dosyalarını yanına koyuyoruz.
            if product_type in ["emlak", "emlak_pro", "crm", "stock", "stok", "stok takibi"]:
                print(f"[{product_type}] Excel Hazırlığı Başlıyor... (Hardcoded Check)")
                
                # HARDCODED PATH CHECK FOR SAFETY
                # Proje yapısına göre kesin yol: C:\Users\alpay\.gemini\antigravity\scratch\alpha_emlak_pro
                # Eğer source_path başka bir şey gelirse diye elle kontrol ekliyoruz.
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                emlak_direct_path = os.path.join(project_root, "alpha_emlak_pro")
                
                target_excels = ["AlphaCraft_Satilik.xlsx", "AlphaCraft_Kiralik.xlsx"]
                
                # 1. Kaynaktan Doğrudan Kopyala
                for exc_name in target_excels:
                    found = False
                    # Önce parametre olarak gelen source_path'e bak
                    src_candidates = [
                        os.path.join(source_path, exc_name),
                        os.path.join(emlak_direct_path, exc_name),
                        os.path.join(app_dir, exc_name) # Belki kopyalanmıştır
                    ]
                    
                    for candidate in src_candidates:
                        if os.path.exists(candidate):
                             out_path = os.path.join(dist_folder, exc_name)
                             shutil.copy2(candidate, out_path)
                             print(f"[{product_type}] Excel Eklendi: {exc_name} (From: {candidate})")
                             found = True
                             break
                    
                    if not found:
                        print(f"[{product_type}] KRİTİK HATA: Excel bulunamadı! {exc_name}")

                # 2. Genel Arama (Yedek)
                import glob
                other_excels = glob.glob(os.path.join(source_path, "*.xlsx"))
                for ox in other_excels:
                    bn = os.path.basename(ox)
                    if bn not in target_excels:
                        shutil.copy2(ox, os.path.join(dist_folder, bn))

            # 7. ZIP Paketle (Dist klasörünü)
            zip_filename = f"Setup_{product_type.upper()}_{license_key}"
            zip_path_no_ext = os.path.join(self.installers_path, zip_filename)
            
            shutil.make_archive(zip_path_no_ext, 'zip', dist_folder)
            
            # Temizlik
            shutil.rmtree(temp_dir)

            return {
                "success": True, 
                "download_url": f"/api/factory/download/{zip_filename}.zip",
                "file_path": f"{zip_path_no_ext}.zip",
                "note": "Compiled Executable Ready"
            }

        except Exception as e:
            # Hata durumunda da temizlik yapmaya calis
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return {"success": False, "error": str(e)}

factory_service = BuildFactory()
