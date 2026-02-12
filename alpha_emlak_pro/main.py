import webview
import json
import os
import threading
import time
from datetime import datetime
import pandas as pd
import sys

# --- EXE UYUMLULUK FONKSİYONU ---
def resource_path(relative_path):
    """ Geliştirme modu için her zaman scriptin olduğu dizini baz al """
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- ALPHA CRAFT PORTFÖY SABİT YOLLAR ---
BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
DATA_FOLDER = os.path.join(BASE_DIR, 'data')

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

EXCEL_PATH = r"C:\AlphaCraft_Emlak"
if not os.path.exists(EXCEL_PATH):
    EXCEL_PATH = BASE_DIR

EXCEL_SATILIK = os.path.join(EXCEL_PATH, "AlphaCraft_Satilik.xlsx")
EXCEL_KIRALIK = os.path.join(EXCEL_PATH, "AlphaCraft_Kiralik.xlsx")

class RealEstateApi:
    def __init__(self):
        self._window = None
        self._sync_thread = None
        self._is_syncing = False
        self.server_url = self._get_server_url()
        
        # Otomatik Güncelleme Kontrolünü Başlat
        threading.Thread(target=self._check_weekly_update, daemon=True).start()

    def set_window(self, window):
        self._window = window

    def _get_server_url(self):
        """config.json dosyasından sunucu adresini okur (Factory standardi)."""
        try:
            # Factory standardi: config.json
            config_path = os.path.join(BASE_DIR, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("server_url", "http://localhost:8001")
            
            # Legacy Fallback
            license_path = os.path.join(BASE_DIR, "license.json")
            if os.path.exists(license_path):
                with open(license_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("server_url", "http://localhost:8001")
        except: pass
        return "http://localhost:8001"

    def _check_weekly_update(self):
        """
        Başlangıçta Excel dosyasının veritabanından yeni olup olmadığını kontrol eder.
        Eğer Excel yeniyse (Azi tarafından güncellenmişse) kullanıcıya buton bildirimi yapar.
        """
        try:
            time.sleep(5) # UI Yüklensin diye bekle
            
            if not os.path.exists(EXCEL_SATILIK): return

            # Dosya zamanlarını karşılaştır
            excel_mtime = os.path.getmtime(EXCEL_SATILIK)
            
            db_path = os.path.join(DATA_FOLDER, 'alpha_database.json')
            db_mtime = 0
            if os.path.exists(db_path):
                db_mtime = os.path.getmtime(db_path)
            
            # Eğer Excel, Veritabanından yeniyse (> 1 dakika fark)
            if excel_mtime > db_mtime + 60:
                print("Tespit: Güncel Excel dosyası mevcut. Kullanıcı uyarılıyor.")
                if self._window:
                     msg = "Azi yeni piyasa verilerini hazırladı! Lütfen Excelleri Güncelle butonuna basınız."
                     self._window.evaluate_js(f"Swal.fire({{toast: true, position: 'top-end', icon: 'info', title: 'Güncelleme Hazır', text: '{msg}', timer: 10000}})")
        except Exception as e:
            print(f"Update Check Error: {e}")

    def save_data(self, collection, data_json):
        """JavaScript'ten gelen verileri JSON dosyası olarak kaydeder."""
        try:
            file_path = os.path.join(DATA_FOLDER, f"{collection}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data_json)
            return True
        except Exception as e:
            print(f"Sistem Kayıt Hatası: {e}")
            return False

    def load_data(self, collection):
        """Kayıtlı verileri diskten okur."""
        try:
            file_path = os.path.join(DATA_FOLDER, f"{collection}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return content if content else "[]"
            return "[]"
        except:
            return "[]"

    # --- ARCHIVE & SYNC METHODS ---
    def upload_document(self, file_path, doc_type, date_str, name):
        """Seçilen dosyayı yapılı klasörlere kopyalar ve veritabanına ekler."""
        import shutil
        import uuid
        try:
            # Klasör Yapısı: data/archives/{TİP}/{TARİH}/{İSİM}/
            dest_folder = os.path.join(DATA_FOLDER, 'archives', doc_type, date_str, name)
            
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            
            # Benzersiz Dosya Adı
            ext = os.path.splitext(file_path)[1]
            original_name = os.path.basename(file_path)
            new_filename = f"{uuid.uuid4().hex[:4]}_{original_name}"
            dest_path = os.path.join(dest_folder, new_filename)
            
            shutil.copy2(file_path, dest_path)
            
            # DB Update
            raw = self.load_data('archives_db')
            archives = json.loads(raw) if raw != "[]" else []
            
            # Göreceli yol (UI'da göstermek ve açmak için)
            # Saklanan Yol: archives/Satış/2023-10-10/Ahmet/dosya.pdf
            rel_path = os.path.join('archives', doc_type, date_str, name, new_filename)
            
            archives.append({
                "filename": new_filename,
                "name": name,
                "type": doc_type,
                "date": date_str,
                "folderPath": rel_path, # Backend'in açması için tam göreceli yol
                "folderDisplay": f"{doc_type} > {date_str} > {name}",
                "originalPath": file_path,
                "fullPath": dest_path
            })
            
            self.save_data('archives_db', json.dumps(archives, ensure_ascii=False))
            return True
        except Exception as e:
            print(f"Archive Error: {e}")
            return False

    def open_document(self, filename, folder_path=None):
        """Arşivdeki dosyayı açar."""
        try:
            if folder_path:
                # Eğer yeni sistemle kaydedilmişse folder_path kullanılır
                path = os.path.join(DATA_FOLDER, folder_path)
            else:
                # Eski sistem (düz klasör)
                path = os.path.join(DATA_FOLDER, 'archives', filename)
                
            if os.path.exists(path):
                os.startfile(path)
                return True
            else:
                print(f"Dosya bulunamadı: {path}")
                return False
        except Exception as e: 
            print(f"Open Error: {e}")
            return False



    def open_folder(self, path):
        """Klasör açar"""
        try:
            os.startfile(path)
        except: pass

    def select_file(self):
        """Dosya seçme diyaloğu açar."""
        if self._window:
            result = self._window.create_file_dialog(webview.OPEN_DIALOG)
            return result[0] if result else None
        return None

    def sync_sale_to_azi(self, listing_no, actual_price, notes):
        """Satışı Azi sunucusuna bildirir."""
        import requests
        try:
            # Not: Gerçek bir lisans anahtarı mekanizması olmalı, şimdilik dummy gönderiyoruz.
            payload = {
                "license_key": "DEMO-KEY", 
                "listing_no": str(listing_no),
                "updates": {
                    "status": "Satıldı",
                    "notes": f"Satış Fiyatı: {actual_price}. Not: {notes}"
                }
            }
            # Localhost varsayıyoruz, prod için domain değişmeli
            requests.post("http://localhost:8001/api/emlak/sale", json=payload, timeout=2)
            return True
        except Exception as e:
            print(f"Server Sync Error: {e}")
            return False

    def run_scraper_bot(self):
        """Azi sunucusundaki botu tetikler."""
        import requests
        try:
            # Botu tetikle
            response = requests.post("http://localhost:8001/api/emlak/run_scraper", timeout=600) # Uzun timeout (bot çalışması için)
            if response.status_code == 200:
                return response.json()
            return {"success": False, "msg": f"Sunucu Hatası: {response.status_code}"}
        except Exception as e:
            print(f"Bot Trigger Error: {e}")
            return {"success": False, "msg": f"Bağlantı Hatası: {e}"}

    def start_sync(self):
        """Excel senkronizasyon motorunu sadece bir kez başlatır."""
        if not self._is_syncing:
            self._is_syncing = True
            self._sync_thread = threading.Thread(target=self._sync_logic, daemon=True)
            self._sync_thread.start()
        return True

    def _clean_price(self, price_val):
        try:
            if isinstance(price_val, (int, float)): return int(price_val)
            cleaned = "".join(filter(str.isdigit, str(price_val)))
            return int(cleaned) if cleaned else 0
        except: return 0

    # --- AI ENGINE ---
    def run_ai_analysis(self, analysis_type):
        """Python tabanlı AI Analiz Motoru."""
        try:
            raw_db = self.load_data('alpha_database')
            data = json.loads(raw_db) if raw_db != "[]" else []
            if not data: return {"title": "Veri Yok", "text": "Henüz analiz edilecek veri bulunmuyor.", "icon": "warning"}

            df = pd.DataFrame(data)
            
            # Fiyat temizliği
            df['price_val'] = df['price'].apply(self._clean_price)
            df['m2_val'] = pd.to_numeric(df['m2'], errors='coerce').fillna(0)

            if analysis_type == 'price':
                # Bölgesel Ortalama
                avg_price = df[df['price_val'] > 0]['price_val'].mean()
                avg_m2 = df[df['price_val'] > 0]['price_val'].sum() / df[df['m2_val'] > 0]['m2_val'].sum()
                
                # Fırsatları bul (Ortalamanın %15 altındakiler)
                opportunities = df[
                    (df['price_val'] > 0) & 
                    (df['price_val'] < avg_price * 0.85)
                ].to_dict('records')

                return {
                    "title": "Fiyat Değerlemesi",
                    "text": f"Bölge Ortalaması: {avg_price:,.0f} TL. En iyi {len(opportunities)} fırsat listelendi.",
                    "icon": "success",
                    "data": opportunities # UI için ham veri
                }

            elif analysis_type == 'speed':
                # İlanların yaş ortalaması
                df['date_dt'] = pd.to_datetime(df['date'], errors='coerce')
                now = datetime.now()
                df['days_active'] = (now - df['date_dt']).dt.days
                avg_days = df['days_active'].mean()
                
                return {
                    "title": "Satış Hızı Analizi",
                    "text": f"Portföydeki ilanların ortalama bekleme süresi {avg_days:.1f} gün. 30 günden eski {len(df[df['days_active'] > 30])} ilan var.",
                    "icon": "info"
                }

            elif analysis_type == 'roi':
                # ROI Hesabı (Kiralık ve Satılık ortalamaları üzerinden)
                satilik = df[df['listingType'] == 'Satılık']['price_val'].mean()
                kiralik = df[df['listingType'] == 'Kiralık']['price_val'].mean()

                if kiralik > 0:
                    amortisman = satilik / (kiralik * 12)
                    roi_percent = (kiralik * 12 / satilik) * 100
                    return {
                        "title": "Yatırım Geri Dönüşü (ROI)",
                        "text": f"Bölge Amortisman Süresi: {amortisman:.1f} Yıl. Yıllık Getiri Oranı: %{roi_percent:.2f}. (Ort. Satılık: {satilik/1000000:.1f}M TL)",
                        "icon": "success"
                    }
                else:
                    return {"title": "Veri Yetersiz", "text": "ROI hesabı için yeterli kiralık ilan verisi yok.", "icon": "warning"}

            elif analysis_type == 'expiry':
                 # Kritik ilanlar
                 return {"title": "Takip Gerektirenler", "text": "Bu modül arayüz üzerinden taranmaktadır.", "icon": "info"}

            elif analysis_type == 'zones':
                # Hot Zones: En hızlı sirkülasyon olan bölgeler
                # (Basitçe: İlan sayısı ve ortalama fiyatına göre popülerlik skoru)
                zone_stats = {}
                for item in data:
                    loc = item.get('location', 'Bilinmiyor')
                    if loc not in zone_stats: zone_stats[loc] = {'count': 0, 'price_sum': 0}
                    zone_stats[loc]['count'] += 1
                    zone_stats[loc]['price_sum'] += self._clean_price(item.get('price', 0))
                
                # Sort by count (popular)
                sorted_zones = sorted(zone_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
                
                text_lines = []
                for z, s in sorted_zones:
                    avg = s['price_sum'] / s['count'] if s['count'] > 0 else 0
                    text_lines.append(f"{z}: {s['count']} İlan (Ort: {avg/1000:.0f}k)")
                
                return {
                    "title": "Sıcak Bölgeler (Hot Zones)",
                    "text": "\n".join(text_lines),
                    "icon": "info"
                }

        except Exception as e:
            return {"title": "Hata", "text": str(e), "icon": "error"}

    def manual_sync(self):
        """Kullanıcı butona bastığında anlık senkronizasyon yapar."""
        try:
            self._perform_sync()
            return {"success": True, "msg": "Veriler güncellendi."}
        except Exception as e:
            return {"success": False, "msg": str(e)}

    def _sync_logic(self):
        """Haftalık değişimleri analiz eden Gelişmiş Senkronizasyon Motoru (Döngü)."""
        while True:
            try:
                self._perform_sync()
            except Exception as e:
                print(f"SYNC LOOP ERROR: {e}")
            time.sleep(60)

    def _perform_sync(self):
        """Tek seferlik veri senkronizasyonu."""
        # CRM Notlarını Önbelleğe Al
        crm_raw = self.load_data('crm_db')
        crm_data = json.loads(crm_raw) if crm_raw != "[]" and crm_raw != "{}" else {}
        
        watch_list = []
        if isinstance(crm_data, dict):
            for l_no, entry in crm_data.items():
                note = entry.get('note', '').lower()
                if '3+1' in note: watch_list.append({'pattern': '3+1', 'contact': l_no})
                if '2+1' in note: watch_list.append({'pattern': '2+1', 'contact': l_no})
                if 'batıkent' in note: watch_list.append({'pattern': 'batıkent', 'contact': l_no})

        try:
            # 1. Mevcut Veriyi Yükle
            raw_db = self.load_data('alpha_database')
            existing_data = json.loads(raw_db) if raw_db != "[]" else []
            
            existing_map = {str(item.get('listingNo', '')): item for item in existing_data}
            
            # Excel'den Gelen Güncel Liste
            current_excel_listings = {} 
            
            files_to_process = [(EXCEL_SATILIK, "Satılık"), (EXCEL_KIRALIK, "Kiralık")]

            for file_path, l_type in files_to_process:
                if os.path.exists(file_path):
                    all_sheets = pd.read_excel(file_path, sheet_name=None)
                    for sheet_name, df in all_sheets.items():
                        df = df.fillna('')
                        category = "İş Yeri" if "Is" in sheet_name or "is" in sheet_name.lower() else "Konut"
                        
                        for _, row in df.iterrows():
                            l_no = str(row.get('İlan No', '')).strip()
                            if not l_no or l_no in ['', 'nan', 'None']: continue
                            
                            new_price = self._clean_price(row.get('Fiyat', 0))
                            location = str(row.get('Konum (İlçe/Mahalle)', row.get('Konum', 'Eskişehir'))).strip()
                            rooms = str(row.get('Oda Sayısı', row.get('Oda', '-'))).strip()
                            
                            # DURUM ANALİZİ
                            status = "Aktif"
                            old_item = existing_map.get(l_no)
                            
                            is_new = False
                            if not old_item: 
                                is_new = True
                                status = "Yeni" # <--- YENİ İLAN STATÜSÜ 
                            
                            if old_item:
                                last_price = int(old_item.get('price', 0))
                                if old_item.get('status') in ['Satıldı', 'Kapora Alındı', 'Pasif']:
                                    status = old_item.get('status') 
                                else:
                                    if new_price < last_price: 
                                        status = "Fiyat Düştü"
                                        # PRICE ALERT
                                        if self._window:
                                            self._window.evaluate_js(f"Swal.fire({{toast: true, position: 'top-end', icon: 'info', title: 'Fiyat Düştü! #{l_no}', text: '{last_price} -> {new_price}', timer: 5000}})")
                                    elif new_price > last_price: status = "Fiyat Arttı"
                            
                            # MATCHMAKER CHECK
                            if is_new and self._window:
                                match_text = (location + " " + rooms).lower()
                                for w in watch_list:
                                    if w['pattern'] in match_text:
                                        self._window.evaluate_js(f"Swal.fire({{toast: true, icon: 'success', title: 'Müşteri Eşleşmesi!', text: 'Aranan kriterde yeni ilan: {l_no} ({w['pattern']})'}})")

                            raw_date = row.get('Yayınlanma Tarihi', row.get('Tarih', ''))
                            date_str = raw_date.isoformat() if hasattr(raw_date, 'isoformat') else str(raw_date)

                            item = {
                                "listingNo": l_no,
                                "title": str(row.get('Başlık', 'Başlıksız')).strip(),
                                "price": new_price,
                                "location": location,
                                "m2": str(row.get('m2 (Brüt)', row.get('m2', '-'))).strip(),
                                "rooms": rooms,
                                "floor": str(row.get('Bulunduğu Kat', row.get('Kat', '-'))).strip(),
                                "phone": str(row.get('Telefon', row.get('İletişim', '-'))).strip(),
                                "type": category,
                                "listingType": l_type,
                                "status": status,
                                "date": date_str,
                                "tags": str(row.get('Etiketler', '')).strip(), # <--- YENİ VERİ
                                "from": "Excel",
                                "last_seen": datetime.now().isoformat()
                            }
                            current_excel_listings[l_no] = item

            # 2. MERGE LOGIC
            final_list = []
            for l_no, item in current_excel_listings.items():
                final_list.append(item)
                
            for l_no, old_item in existing_map.items():
                if l_no not in current_excel_listings:
                    current_status = old_item.get('status', 'Aktif')
                    if current_status not in ['Satıldı', 'Dosyadan Kalktı']:
                        current_status = 'Dosyadan Kalktı' # Düzeltme
                        old_item['status'] = 'Dosyadan Kalktı'
                    final_list.append(old_item)

            data_to_save = json.dumps(final_list, ensure_ascii=False)
            self.save_data('alpha_database', data_to_save)
            
            if self._window:
                self._window.evaluate_js(f"if(window.APP && typeof window.APP.receiveData === 'function') {{ window.APP.receiveData({data_to_save}); }}")

            # --- AUTO REMINDER CHECK ---
            self.check_reminders()

        except Exception as e:
            print(f"SYNC HATA: {e}")
            if self._window and 'data_to_save' in locals():
                self._window.evaluate_js(f"if(window.APP && typeof window.APP.receiveData === 'function') {{ window.APP.receiveData({data_to_save}); }}")

    # --- DOCUMENT INTELLIGENCE & REMINDERS ---
    def analyze_document(self, file_path):
        """
        Belgeyi analiz eder (OCR, PDF Text, Regex).
        Geri dönüş: { "date": "...", "amount": "...", "type": "...", "text": "..." }
        """
        import re
        result = {"date": "", "amount": "", "type": "Diğer", "text": ""}
        
        # 1. Dosya Varlığı Kontrolü
        if not os.path.exists(file_path):
            # Göreceli yol verilmiş olabilir, tam yolu bulalım
            file_path = os.path.join(DATA_FOLDER, file_path)
            if not os.path.exists(file_path):
                return {"error": "Dosya bulunamadı"}

        filename = os.path.basename(file_path).lower()
        content_text = ""

        # 2. Dosya Tipine Göre Okuma
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.pdf':
                try:
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    for page in reader.pages:
                        content_text += page.extract_text() + "\n"
                except ImportError:
                    print("pypdf kütüphanesi yok, PDF metin analizi atlandı.")
                except Exception as e:
                    print(f"PDF Okuma Hatası: {e}")

            elif ext in ['.jpg', '.jpeg', '.png']:
                try:
                    from PIL import Image
                    import pytesseract
                    # Tesseract path windows default (Kullanıcıda varsa)
                    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                    img = Image.open(file_path)
                    content_text = pytesseract.image_to_string(img, lang='tur+eng')
                except ImportError:
                    print("OCR kütüphaneleri (Pillow, pytesseract) yok.")
                except Exception as e:
                    print(f"OCR Hatası (Tesseract kurulu olmayabilir): {e}")

        except Exception as e:
            print(f"Analiz Genel Hatası: {e}")

        # Eğer içerik boşsa dosya ismini kullan
        if not content_text.strip():
            content_text = filename

        result["text"] = content_text[:500] + "..." # Önizleme için

        # 3. Akıllı Veri Çıkarımı (Regex)
        
        # TÜR TAHMİNİ
        if "kira" in filename or "kira" in content_text.lower(): result["type"] = "Kira"
        elif "satış" in filename or "satis" in filename or "satış" in content_text.lower(): result["type"] = "Satış"
        elif "senet" in filename or "bono" in content_text.lower(): result["type"] = "Senet"
        elif "tapu" in filename or "tapu" in content_text.lower(): result["type"] = "Tapu"

        # TARİH TAHMİNİ (DD.MM.YYYY veya YYYY-MM-DD)
        date_pattern = r'\b(\d{1,2})[.-/](\d{1,2})[.-/](\d{2,4})\b'
        dates = re.findall(date_pattern, content_text)
        if dates:
            # İlk bulunan tarihi al (Genelde evrak tarihi üstte olur)
            d = dates[0] 
            # Yıl tamamlama (23 -> 2023)
            year = d[2]
            if len(year) == 2: year = "20" + year
            # Format: YYYY-MM-DD (Input date value formatı)
            try:
                # Olası formatlar: gün/ay/yıl
                dt = datetime(int(year), int(d[1]), int(d[0]))
                result["date"] = dt.strftime("%Y-%m-%d")
            except: pass
        else:
            # Bugünün tarihini varsayılan yap
            result["date"] = datetime.now().strftime("%Y-%m-%d")

        # TUTAR TAHMİNİ
        # Örn: 10.000 TL, 10000TL, 15,000.00
        amount_pattern = r'(\d{1,3}(?:[.,]\d{3})*)(?:\s?TL|\s?USD|\s?\$|\s?EUR|\s?€)'
        amounts = re.findall(amount_pattern, content_text, re.IGNORECASE)
        if amounts:
            # En büyük sayıyı bul (Muhtemelen ana tutardır)
            valid_amounts = []
            for amt in amounts:
                clean = amt.replace('.', '').replace(',', '.')
                try: valid_amounts.append(float(clean))
                except: pass
            if valid_amounts:
                result["amount"] = int(max(valid_amounts))
        
        return result

    def save_reminder(self, reminder_data):
        """Kullanıcı onaylı hatırlatıcıyı kaydeder."""
        try:
            # Beklenen Data: { "title": "Ahmet Kira", "date": "2024-05-01", "type": "Kira", "amount": 15000, "file": "..." }
            reminder_data["id"] = str(datetime.now().timestamp())
            reminder_data["status"] = "active"
            reminder_data["created_at"] = datetime.now().isoformat()
            
            raw = self.load_data('reminders_db')
            reminders = json.loads(raw) if raw != "[]" else []
            reminders.append(reminder_data)
            
            self.save_data('reminders_db', json.dumps(reminders, ensure_ascii=False))
            return True
        except Exception as e:
            print(f"Reminder Save Error: {e}")
            return False

    def get_reminders(self):
        """Aktif hatırlatıcıları döndürür."""
        return json.loads(self.load_data('reminders_db'))

    def delete_reminder(self, r_id):
        """Hatırlatıcı siler/tamamlar."""
        try:
            raw = self.load_data('reminders_db')
            reminders = json.loads(raw) if raw != "[]" else []
            reminders = [r for r in reminders if r.get("id") != r_id]
            self.save_data('reminders_db', json.dumps(reminders, ensure_ascii=False))
            return True
        except: return False

    def check_reminders(self):
        """Periyodik olarak hatırlatmaları kontrol eder ve UI'a bildirir."""
        if not self._window: return
        
        try:
            raw = self.load_data('reminders_db')
            reminders = json.loads(raw) if raw != "[]" else []
            
            today = datetime.now().date()
            notifications = []

            for r in reminders:
                if r.get("status") != "active": continue
                
                target_date_str = r.get("date")
                if not target_date_str: continue

                try:
                    target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
                    delta = (target_date - today).days
                    
                    # Bildirim Mantığı
                    msg = ""
                    if delta == 0: msg = f"BUGÜN: {r.get('title')} ödemesi var! ({r.get('amount')} TL)"
                    elif delta == 1: msg = f"YARIN: {r.get('title')} ödemesi."
                    elif delta == 3: msg = f"3 Gün Kaldı: {r.get('title')}"
                    elif delta < 0: msg = f"GECİKTİ ({abs(delta)} gün): {r.get('title')}"
                    
                    if msg:
                        notifications.append(msg)
                        # JS tarafında toast göster
                        safe_msg = msg.replace("'", "")
                        self._window.evaluate_js(f"if(window.APP) window.APP.showNotification('{safe_msg}', 'warning')")

                except: pass
            
            # Eğer bildirim varsa Azi'ye de (Console log olarak) düşebilir
            if notifications:
                print(f"Reminder Alerts: {notifications}")

        except Exception as e:
            print(f"Check Reminder Error: {e}")

def start_app():
    api = RealEstateApi()
    window = webview.create_window(
        title='Alpha Craft Portföy v2.0',
        url=resource_path('index.html') + f"?v={int(time.time())}",
        js_api=api,
        width=1400,
        height=900,
        background_color='#010409'
    )
    api.set_window(window)
    # --- TELEMETRY START ---
    try:
        import telemetry
        license_key = "DEMO_EMLAK_001"
        license_path = os.path.join(BASE_DIR, "license.key")
        if os.path.exists(license_path):
            with open(license_path, "r") as f: license_key = f.read().strip()
            
        t_worker = telemetry.TelemetryWorker(license_key, "AlphaEmlak", DATA_FOLDER, api, api.server_url)
        t_worker.start()
        print("Emlak Telemetry Active.")
    except Exception as e:
        print(f"Telemetry Failed: {e}")
    # -----------------------

    webview.start(debug=True)

if __name__ == '__main__':
    start_app()