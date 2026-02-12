import time
import os
import random
import pandas as pd
import pandas as pd
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    CHROME_AVAILABLE = True
except ImportError:
    uc = None
    By = None
    CHROME_AVAILABLE = False
    print("[AutomatedScraper] Uyarı: Selenium/Chrome modülleri eksik. Scraper çalışmayacak.")

# --- CONFIG ---
APP_FOLDER = r"C:\AlphaCraft_Emlak"
if not os.path.exists(APP_FOLDER):
    try:
        os.makedirs(APP_FOLDER)
    except:
        pass # Yetki sorunu vb. varsa loglanmalı

TASKS = [
    {
        "file": "AlphaCraft_Satilik.xlsx",
        "sheet": "Konut",
        "url": "https://www.sahibinden.com/satilik/sahibinden?view=detailed&pagingSize=50&address_town=330&address_town=329&address_city=26"
    },
    {
        "file": "AlphaCraft_Satilik.xlsx",
        "sheet": "Is_Yeri",
        "url": "https://www.sahibinden.com/satilik-is-yeri?view=detailed&pagingSize=50&address_town=330&address_town=329&address_city=26"
    },
    {
        "file": "AlphaCraft_Kiralik.xlsx",
        "sheet": "Konut",
        "url": "https://www.sahibinden.com/kiralik/sahibinden?view=detailed&pagingSize=50&address_town=330&address_town=329&address_city=26"
    },
    {
        "file": "AlphaCraft_Kiralik.xlsx",
        "sheet": "Is_Yeri",
        "url": "https://www.sahibinden.com/kiralik-is-yeri?view=detailed&pagingSize=50&a27=38460&viewType=Gallery&address_town=330&address_town=329&address_city=26"
    }
]

class ScraperBot:
    def __init__(self):
        self.driver = None

    def setup_driver(self):
        options = uc.ChromeOptions()
        # temp_profile = os.path.join(APP_FOLDER, "Alpha_Master_Profile")
        # options.add_argument(f"--user-data-dir={temp_profile}")
        options.add_argument("--disable-gpu")
        # options.add_argument("--headless") # Headless modda çalıştırılabilir
        options.add_argument("--no-sandbox")
        
        try:
            self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=144)
            return True
        except Exception as e:
            print(f"[Scraper] Driver Init Error: {e}")
            return False

    def handle_popups(self):
        try:
            selectors = ["#onetrust-accept-btn-handler", "//button[text()='Kabul Et']", "//button[contains(text(),'Tamam')]"]
            for s in selectors:
                try:
                    el = self.driver.find_element(By.CSS_SELECTOR if s.startswith("#") else By.XPATH, s)
                    el.click()
                    time.sleep(1)
                except: pass
        except: pass

    def run(self):
        print("[Scraper] Bot Started...")
        if not self.setup_driver():
            return {"success": False, "msg": "Driver başlatılamadı"}

        storage = {}
        try:
            self.driver.maximize_window()
            
            for task in TASKS:
                file_name = task["file"]
                sheet_name = task["sheet"]
                base_url = task["url"]
                
                if file_name not in storage: storage[file_name] = {}
                storage[file_name][sheet_name] = []

                print(f"[Scraper] Processing: {file_name} -> {sheet_name}")
                
                # Sayfaları tara (2500 ilan limiti - Yaklaşık 50 sayfa)
                for offset in range(0, 2500, 50): 
                    current_url = f"{base_url}&pagingOffset={offset}"
                    self.driver.get(current_url)
                    print("Sayfa yüklendi. Captcha çıkarsa lütfen çözün, 20 saniye bekleniyor...")
                    time.sleep(20) # Kullanıcıya fırsat tanı
                    # time.sleep(random.uniform(4, 7)) # Eski kısa bekleme
                    self.handle_popups()

                    rows = self.driver.find_elements(By.CSS_SELECTOR, ".searchResultsItem")
                    if not rows:
                        # Eğer hiç veri yoksa veya sayfa boşsa (bazen yüklenmez) tekrar dene
                        print("[Scraper] Rows not found, retrying...")
                        time.sleep(5)
                        rows = self.driver.find_elements(By.CSS_SELECTOR, ".searchResultsItem")
                    
                    if not rows:
                        print(f"[Scraper] No more rows at offset {offset}, breaking.")
                        break

                    for row in rows:
                        try:
                            ad_id = row.get_attribute("data-id")
                            if not ad_id: continue
                            cols = row.find_elements(By.TAG_NAME, "td")
                            title_el = row.find_element(By.CSS_SELECTOR, ".searchResultsTitleValue a")
                            
                            data = {
                                "listingNo": ad_id, # 'İlan No' yerine 'listingNo' standartlaştıralım
                                "title": title_el.text.strip(),
                                "m2": cols[2].text.strip() if len(cols) > 2 else "N/A",
                                "rooms": cols[3].text.strip() if len(cols) > 3 else "N/A",
                                "price": row.find_element(By.CSS_SELECTOR, ".searchResultsPriceValue").text.strip(),
                                "location": row.find_element(By.CSS_SELECTOR, ".searchResultsLocationValue").text.strip().replace("\n", " "),
                                "date": row.find_element(By.CSS_SELECTOR, ".searchResultsDateValue").text.strip().replace("\n", " "),
                                "url": title_el.get_attribute("href"),
                                "type": sheet_name
                            }
                            
                            # Ekstra Bilgi: Etiketler (Güvenli)
                            try:
                                icons = row.find_elements(By.CSS_SELECTOR, ".searchResultsAttributeIcons li")
                                tag_list = [icon.get_attribute("title") for icon in icons if icon.get_attribute("title")]
                                data["tags"] = ", ".join(tag_list)
                            except: data["tags"] = ""

                            # Eski Key Uyumluluğu ve Yeni Kolonlar
                            data["Etiketler"] = data.get("tags", "")
                            # Eski Key Uyumluluğu (Gerekirse)
                            data["İlan No"] = data["listingNo"]
                            data["Fiyat"] = data["price"]
                            
                            storage[file_name][sheet_name].append(data)
                        except: continue

            # Excel Kaydetme
            # 1. C:\AlphaCraft_Emlak (Server Runtime Path)
            # 2. Project Source Path (Factory Build Path)
            
            # Proje Kaynak Klasörünü Bul (Development Env)
            # Şu anki dosya: azi_server/brain/products/automated_scraper.py
            # Hedef: alpha_emlak_pro (scratch root altında)
            current_script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_script_dir))))
            # scratch klasörüne kadar çıktık (tahmini) - garanti olsun diye absolute path verelim veya user root
            # Garanti yol:
            development_source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "alpha_emlak_pro")
            
            target_folders = [APP_FOLDER]
            if os.path.exists(development_source_path):
                target_folders.append(development_source_path)
                print(f"[Scraper] Ek Hedef Eklendi: {development_source_path}")

            for file_name, sheets in storage.items():
                # Her hedef klasör için kaydet
                for folder in target_folders:
                    file_path = os.path.join(folder, file_name)
                    try:
                        import openpyxl
                        # Veri var mı kontrol et
                        has_data = False
                        for _, data in sheets.items():
                            if data: has_data = True; break
                        
                        if not has_data:
                            print(f"[Scraper] Uyarı: {file_name} için veri bulunamadı. Boş dosya oluşturuluyor.")
                            # Boş dosya hatasını önlemek için dummy sheet
                            sheets["Rapor"] = [{"Durum": "Veri Bulunamadı", "Tarih": time.strftime("%d.%m.%Y %H:%M")}]

                        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                            data_written = False
                            for sheet_name, data_list in sheets.items():
                                df = pd.DataFrame(data_list)
                                # Boş olsa bile sheet oluştur ki "No visible sheet" hatası almasın
                                if df.empty:
                                    df = pd.DataFrame([{"Durum": "Veri Yok"}])
                                
                                print(f"[Scraper] Writing {len(data_list)} items to {sheet_name}")
                                df.drop_duplicates(subset=['listingNo'], inplace=True) if 'listingNo' in df.columns else None
                                df.to_excel(writer, sheet_name=sheet_name, index=False)
                                data_written = True
                            
                            if not data_written:
                                 # Hiç sheet eklenmediyse dummy ekle (Tekrar garanti olsun)
                                 pd.DataFrame([{"Info": "Empty"}]).to_excel(writer, sheet_name="Info", index=False)

                    except Exception as e:
                        print(f"[Scraper] Excel Save Error ({file_name}): {e}")
                        return {"success": False, "msg": f"Excel hatası: {e}"}

            return {"success": True, "msg": "Veriler başarıyla güncellendi."}

        except Exception as e:
            return {"success": False, "msg": f"Genel hata: {e}"}
        finally:
            print("[Scraper] İşlem bitti.")
            try:
                self.driver.quit() 
            except: pass

bot_instance = ScraperBot()

if __name__ == "__main__":
    bot_instance.run()
