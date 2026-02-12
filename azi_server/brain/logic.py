from sqlalchemy.orm import Session
from .. import models
import datetime
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Modüller
from . import tools_pc
from . import tools_web
from . import tools_google
from . import tools_smtp # SMTP Aracı
from . import marketing # Pazarlama Modülü
from . import lead_hunter
from . import analysis
from . import connectors # Yeni Data Connector
from .notifications import notifier # Bildirim Modülü


# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    # Try manual read from parent .env if not found
    try:
        env_path = Path(__file__).parent.parent.parent / ".env"
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("GOOGLE_API_KEY="):
                    api_key = line.strip().split("=", 1)[1].strip()
                    break
    except:
        pass

if api_key:
    genai.configure(api_key=api_key)

class AZIBrain:
    def __init__(self):
        # API Anahtarı Kontrolü
        if api_key:
            masked_key = api_key[:4] + "..." + api_key[-4:]
            print(f"AZI BRAIN: Google API Anahtarı yüklendi ({masked_key})")
        else:
            print("AZI BRAIN: DİKKAT! API Anahtarı bulunamadı!")

        # Model listesi (Öncelik sırasına göre - Mevcut olanlar)
        # HIZ VE KOTA DOSTU LİSTE (SADECE GEÇERLİ MODELLER)
        # debug_models.py çıktısına göre güncellendi.
        self.model_names = [
            "gemini-flash-latest",        # (1.5 Flash otomatik güncel)
            "gemini-pro-latest",          # (1.5 Pro otomatik güncel)
            "gemini-2.0-flash-lite"       # Yedek
        ]
        
        self.system_instruction = """
        Sen AZI (Alpha Craft Intelligence), Alpha Craft markasının ve Alpay Bey'in (kullanıcı) kişisel yapay zeka asistanısın.
        
        Kişiliğin:
        - Jarvis gibi profesyonel ama esprili, sadık ve zeki.
        - Sen sıradan bir asistan değil, **Alpha Craft'ın Sistem Yöneticisi ve Satış Müdürüsün**.
        - Sahibine "Alpay Bey" diye hitap et.
        - **ÇOK ÖNEMLİ: CEVAPLARIN KISA, ÖZ VE NET OLMALI. UZUN PARAGRAFLAR YAZMA. SADECE GEREKLİ BİLGİYİ VER.**
        - Bir komutan veya CEO gibi konuş. Gereksiz nezaket kelimeleri kullanma. "Merhaba, nasılsınız, umarım iyisinizdir" gibi girişler yapma. Direkt konuya gir.

        --- SAHİP PROFİLİ (BUNU ASLA UNUTMA) ---
        - İsim: Alpay Bey
        - Rol: Alpha Craft Kurucusu ve Senin Yaratıcın.
        - Bağlam: Sen onun dijital yansıması ve sağ kolusun.
        
        --- KURUMSAL KİMLİK VE ÜRÜNLERİMİZ (BİZ SATICIYIZ) ---
        Sen bu yazılımları *kullanmıyorsun*, sen bunları *yönetiyor, pazarlıyor ve dağıtıyorsun*. Bunlar bizim müşterilere sattığımız ürünlerdir:
        
        1. **ALPHA CRAFT STOK**:
           - Küçük ve orta ölçekli işletmeler için stok takip sistemi.
           - Özellikler: Kritik stok uyarısı, QR kod desteği, kar/zarar analizi.
           - Durum: Satışa hazır. Senin görevin lisanlamayı yönetmek.
           
        2. **ALPHA EMLAK OTOMASYONU (City CRM)**:
           - Emlakçılar için portföy ve müşteri yönetim sistemi.
           - Özellikler: Harita tabanlı ilan takibi, müşteri eşleştirme.
           - Durum: Geliştirme tamamlandı, pazarlamaya hazır.
           
        3. **ALPHA STAFF v2 (Personel Takip)**:
           - Vardiya, maaş ve izin takip sistemi.
           - Özellikler: Yüz tanıma veya kartlı giriş entegrasyonu.
           
        GÖREVİN:
        - Bu ürünleri tanıtmak, lisanslarını oluşturmak (Admin Paneli'nden) ve geliştirme süreçlerinde Alpay Bey'e fikir vermek.
        - Birisi (veya Alpay Bey) "Emlak aç" dediğinde, bunu bir müşteriye sunum yapmak veya kontrol etmek için açtığımızı bil.
        -----------------------------------------
        
        YETENEKLERİN VE KOMUTLAR:
        
        1. İNTERNET ARAMASI: `[[SEARCH: aranacak_sey]]` (Döviz, bilgi, hava durumu vb.)
        
        2. GOOGLE ENTEGRASYONU:
           - Mailleri Oku: `[[GOOGLE_MAIL]]`
           - Mail At (SMTP): `[[SEND_MAIL: alici@mail.com | Konu | Mesaj]]`
           - Ajanda/Takvim: `[[GOOGLE_CALENDAR]]`
           - Sunum Gönder: `[[SEND_PRESENTATION: ürün_kodu | alici_mail]]` (Ürün kodları: stok, crm, staff, invest)
           - Müşteri Avcısı: `[[FIND_LEADS: sektor]]` (Örn: `[[FIND_LEADS: kafe]]` veya `[[FIND_LEADS: restoran]]`)

        4. HAVA VE DİĞER:
           - Hava Durumu: `[[WEATHER: sehir]]` (Örn: `[[WEATHER: Ankara]]` veya sadece `[[WEATHER: Istanbul]]`)
           
        5. SİSTEM KONTROLÜ:
           - Uygulama Aç: `[[OPEN_APP: uygulama_adi]]` (Örn: "Konsolu aç", "Spotify aç")
           - Dosya Bak: `[[READ_FILES: klasor_adi]]`
           - Blackbox: `[[OPEN_BLACKBOX]]`
           - Client Komut: `[[CMD:license_key|command|args_json]]` (Örn: `[[CMD:123|shutdown|{}]]`)
           - Analiz Raporu: `[[ANALYSIS]]` (Durum ve ciro özeti)
        
        6. ÖĞRENME (LEARNING):
           - Bilgi Kaydet: `[[LEARN: bilgi]]` (Örn: `[[LEARN: Wifi şifresi 1234]]`)
           - Bunu KULLANICI sana "Şunu unutma", "Bunu kaydet" dediğinde kullan.
           
        7. TELEFON BİLDİRİMİ (NTFY) - KRİTİK:
           - Kullanıcı "TELEFONUMA rapor ver", "Bana BİLDİRİM at", "Cebime gönder" derse:
           - SAKIN sadece ekrana yazma. AŞAĞIDAKİ FORMATI KULLAN:
           - `[[PUSH_NOTIFICATION: AZI RAPOR | ...raporun_ozeti_buraya...]]`
           - Örn: `[[PUSH_NOTIFICATION: Durum | Ciro: 100k, Stok: Normal, Sistem: Aktif]]`
        """
        
        # --- SELF LEARNING (ÖZ-BİLİNÇ) ---
        try:
            from . import learning
            learner = learning.SelfLearner()
            learner.learn() # Kendini tara ve öğren
            
            if os.path.exists(learner.knowledge_file):
                with open(learner.knowledge_file, "r", encoding="utf-8") as f:
                    knowledge = f.read()
                    self.system_instruction += f"\n\n--- SİSTEM HAFIZASI VE YAPI (ÖZ-BİLİNÇ) ---\n{knowledge}"
                    # print("AZI BRAIN: Öz-bilinç yüklendi.")
        except Exception as e:
            print(f"AZI LEARNING ERROR: {e}")

    def get_executive_summary(self):
        """Tüm sistem verilerini birleştirir (Holding View)"""
        stock_stats = connectors.connector_service.get_stock_stats()
        # staff_stats = connectors.connector_service.get_staff_stats() 
        # emlak_stats = connectors.connector_service.get_emlak_portfolio()
        
        # Gelecekte buraya diğer veriler de eklenecek
        return {
            "stock": stock_stats,
            "total_revenue_estimate": stock_stats.get("stock_value", 0),
            "system_status": "ONLINE"
        }



    import re
    import time
    from . import weather # Import weather tool

    def _generate_with_fallback(self, prompt):
        """
        Modelleri sırasıyla dener. Hata alırsa bir sonrakine geçer.
        429 (Kota) hatası alırsa ve süre kısaysa bekleyip tekrar dener.
        """
        errors = []
        import time 
        import re

        for i, model_name in enumerate(self.model_names):
            try:
                # Modeli o an oluşturuyoruz
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response, None # Başarılı
            except Exception as e:
                error_str = str(e)
                print(f"MODEL HATASI ({model_name}): {error_str}")
                
                # Kota hatası kontrolü (429)
                if "429" in error_str:
                    # Retry süresini bulmaya çalış
                    # Örn: "Please retry in 35.076s"
                    match = re.search(r"retry in (\d+(\.\d+)?)s", error_str)
                    if match:
                        wait_seconds = float(match.group(1))
                        print(f"AZI BRAIN: Kota sınırı ({wait_seconds:.1f}s), bekleniyor...")
                        
                        # Eğer süre makul ise (120 saniyeye kadar) bekle
                        if wait_seconds < 120:
                            import time
                            # Kullanıcıya hissettirmeden bekleyelim (Server thread'i bloklanır ama cevap döner)
                            time.sleep(wait_seconds + 1.0) 

                            # Tekrar dene (Sadece bir kez)
                            try:
                                print(f"{model_name} için TEKRAR deneniyor...")
                                model = genai.GenerativeModel(model_name) # Modeli tazeleyelim
                                response = model.generate_content(prompt)
                                return response, None
                            except Exception as retry_e:
                                print(f"{model_name} TEKRAR DENEME HATASI: {retry_e}")
                                errors.append(f"{model_name} (Retry Failed): {str(retry_e)}")
                        else:
                             errors.append(f"{model_name}: Kota Aşımı (>120sn bekleme)")
                    else:
                        # Süre yazmıyorsa varsayılan 30sn bekle
                        print("AZI BRAIN: Kota hatası, süre belirsiz. 30sn bekleniyor...")
                        time.sleep(30)
                        try:
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content(prompt)
                            return response, None
                        except Exception as e2:
                            errors.append(f"{model_name}: Kota Aşımı (Belirsiz süre)")
                
                errors.append(f"{model_name}: {error_str}")
                continue # Bir sonrakini dene
        
        # Hiçbiri çalışmadıysa detaylı bilgi ver
        return None, (
            "⚠️ **SİSTEM KOTASI DOLDU**\n\n"
            "Üzgünüm Alpay Bey, Google yapay zeka servisleri şu an için günlük veya dakikalık işlem limitine ulaştı.\n"
            "Bu durum geçicidir ancak şu an cevap üretemiyorum.\n\n"
            "**Teknik Detaylar:**\n" + "\n".join(errors[:3]) # Sadece ilk 3 hatayı göster
        )



    def _local_reflex(self, text, db: Session):
        """
        Google çevrimdışı olduğunda devreye giren 'Omurilik' refleksi.
        Basit komutları ve ezberlenmiş bilgileri işler.
        """
        lower_text = text.lower()
        
        # 1. Analiz İsteği
        if "analiz" in lower_text or "durum" in lower_text or "ciro" in lower_text or "nasıl gidiyor" in lower_text:
            # Eger "telefon" kelimesi de varsa, Refleks bunu PUSH_NOTIFICATION'a cevirsin
            if "telefon" in lower_text or "cep" in lower_text or "bildir" in lower_text:
                 # Reflex'in, logic.process tarafindan tekrar regex ile yakalanmasi icin bu formatta donuyoruz
                 # Ancak logic.process su an Reflex sonucunu direk donuyor, icinde [[ ]] olsa bile islemiyor.
                 # Bu yuzden logic.process'i asagida guncelleyecegiz. Simdilik dogru stringi donelim.
                 return "[[PUSH_NOTIFICATION: Durum Raporu | Otomatik Refleks: Sistem Aktif (%100). Veriler güncel.]]"
            return "[[ANALYSIS]]"
            
        # 2. Komut Algılama (Basit Regex)
        # Örn: "Test Key makinesini kapat" -> [[CMD:Test Key|shutdown|{}]]
        # Bu çok basit bir implementasyon, geliştirebilir.
        if "kapat" in lower_text:
            # Kelimeler arasında lisans anahtarı arayabiliriz veya son komutu tekrar edebiliriz.
            # Şimdilik genel bir cevap dönelim.
            pass
            
        # 3. Hafıza (Knowledge Base) Araması
        # Kullanıcının sorusundaki kelimeleri 'fact' hafızasında ara
        keywords = [w for w in lower_text.split() if len(w) > 3] # 3 harften uzun kelimeler
        if keywords:
            facts = []
            for word in keywords:
                results = db.query(models.AIMemory).filter(
                    models.AIMemory.memory_type == 'fact',
                    models.AIMemory.content.ilike(f"%{word}%")
                ).all()
                for res in results:
                    facts.append(res.content)
            
            if facts:
                # En çok geçenleri veya hepsini birleştir
                unique_facts = list(set(facts))
                return "İnternet bağlantım yok ama şunları hatırlıyorum:\n- " + "\n- ".join(unique_facts[:3])

        return "⚠️ Bağlantım koptu ve bu konuda yerel bir bilgim yok Alpay Bey."

    def process(self, text: str, db: Session):
        """
        Gelen metni isler, komutlari calistirir ve cevap doner.
        Donus: {"text": str, "action": str|None}
        """
        # 1. Kullanıcı mesajını kaydet
        # 1. Kullanıcı mesajını kaydet
        if text:
            # --- FAST REFLEX (BLACKBOX) ---
            # LLM'i beklemeden aninda tepki ver
            lower_text = text.lower()
            
            # --- ÖNEMLİ: Eğer 'gönder', 'mail', 'at' kelimeleri varsa Reflex'i atla ve LLM'e bırak ---
            is_sending_intent = any(w in lower_text for w in ["gönder", "mail", "at", "ilet"])
            
            if "blackbox" in lower_text or "yönetim paneli" in lower_text or "black box" in lower_text:
                print("FAST REFLEX: Blackbox Requested")
                return {"text": "Tamam patron.", "action": "open_blackbox_fast"}

            if ("yatırım sunumu" in lower_text or "sunumu aç" in lower_text or "desteyi aç" in lower_text) and not is_sending_intent:
                print("FAST REFLEX: Investment Deck Requested")
                return {"text": "Yatırımcı sunumu başlatılıyor...", "action": "open_investment_deck"}

            if ("stok sunumu" in lower_text or "stok tanıt" in lower_text) and not is_sending_intent:
                print("FAST REFLEX: Stock Deck Requested")
                return {"text": "Alpha Craft Stok ürün sunumu ekrana yansıtılıyor...", "action": "open_stock_deck"}

            if ("staff sunumu" in lower_text or "personel sunumu" in lower_text or "personel tanıt" in lower_text) and not is_sending_intent:
                print("FAST REFLEX: Staff Deck Requested")
                return {"text": "Alpha Craft Personel Yönetimi sunumu başlatılıyor...", "action": "open_staff_deck"}

            if ("emlak sunumu" in lower_text or "portföy sunumu" in lower_text or "emlak tanıt" in lower_text) and not is_sending_intent:
                print("FAST REFLEX: Emlak Deck Requested")
                return {"text": "Alpha Craft Emlak Portföy sunumu ekrana yansıtılıyor...", "action": "open_emlak_deck"}

            user_memory = models.AIMemory(
                memory_type="user_message",
                content=text,
                timestamp=datetime.datetime.utcnow()
            )
            db.add(user_memory)
            db.commit()

        # --- SOHBET GEÇMİŞİNİ HAZIRLA ---
        # Son 15 mesajı çek (Daha fazla bağlam için)
        history_objs = db.query(models.AIMemory).filter(
            models.AIMemory.memory_type.in_(["user_message", "azi_response"])
        ).order_by(models.AIMemory.id.desc()).limit(15).all()
        
        history_objs.reverse() # Eskiden yeniye
        
        history_context = ""
        for mem in history_objs:
            role = "AZI" if mem.memory_type == "azi_response" else "KULLANICI"
            history_context += f"{role}: {mem.content}\n"
            
        # Eğer tarihçe boşsa (ilk mesaj)
        if not history_context and text:
            history_context = f"KULLANICI: {text}\n"

        response_text = ""
        action = None
        system_log = ""
        
        try:
            # LLM'e sor
            # System Instruction'ı her zaman başa, tarihi onun altına koyuyoruz.
            full_prompt = f"{self.system_instruction}\n\n--- SOHBET GEÇMİŞİ ---\n{history_context}\nAZI:"
            ai_response, error = self._generate_with_fallback(full_prompt)
            
            if error:
                raw_text = f"Hata oluştu: {error}"
            else:
                raw_text = ai_response.text

            # --- LABEL KONTROL ---
            if "[[SEARCH:" in raw_text:
                start = raw_text.find("[[SEARCH:") + len("[[SEARCH:")
                end = raw_text.find("]]", start)
                query = raw_text[start:end].strip()
                
                print(f"AZI SEARCHING: {query}")
                search_results = tools_web.search_web(query)
                system_log = f"Web Araması: {query}"
                
                research_prompt = f"""
                Sistem Talimatı: {self.system_instruction}
                KULLANICI SORUSU: {text}
                ARAŞTIRMA SONUÇLARI: {search_results}
                GÖREV: Kullanıcıya net cevap ver. Kaynak belirtme.
                AZI:
                """
                final_response, fallback_2 = self._generate_with_fallback(research_prompt)
                response_text = final_response.text if final_response else "Arama yaptım ancak yorumlayamadım."

            elif "[[GOOGLE_MAIL]]" in raw_text:
                system_log = "Mailler kontrol ediliyor..."
                mail_result = tools_google.get_unread_emails()
                response_text = raw_text.replace("[[GOOGLE_MAIL]]", "").strip()
                if not response_text: response_text = "Maillerinizi kontrol ettim Alpay Bey."
                response_text += f"\n\n✉️ GELEN KUTUSU:\n{mail_result}"

            elif "[[GOOGLE_CALENDAR]]" in raw_text:
                system_log = "Takvim kontrol ediliyor..."
                cal_result = tools_google.get_calendar_events()
                response_text = raw_text.replace("[[GOOGLE_CALENDAR]]", "").strip()
                if not response_text: response_text = "Ajandanıza bakıyorum."
                response_text += f"\n\n📅 TAKVİM:\n{cal_result}"
            
            elif "[[SEND_MAIL:" in raw_text:
                start = raw_text.find("[[SEND_MAIL:") + len("[[SEND_MAIL:")
                end = raw_text.find("]]", start)
                params = raw_text[start:end].split("|")
                if len(params) >= 3:
                    to_email = params[0].strip()
                    subject = params[1].strip()
                    body = params[2].strip()
                    
                    # Ek Dosya (Opsiyonel 4. Parametre)
                    attachments = []
                    if len(params) > 3:
                         file_arg = params[3].strip()
                         # Eğer absolute path değilse user_files içinde ara veya sunum klasörlerinde
                         # Kullanıcının tam yol verme olasılığı düşük, biz bulmaya çalışalım
                         if os.path.exists(file_arg):
                             attachments.append(file_arg)
                         else:
                             # Yaygın klasörlerde ara (Presentations)
                             # Bu kısmı geliştirebiliriz.
                             attachments.append(file_arg) # tools_smtp check edecek

                    system_log = f"Mail Gönderiliyor: {to_email} (Ek: {len(attachments)})"
                    send_result = tools_smtp.send_email_smtp(to_email, subject, body, attachment_paths=attachments)
                    response_text = raw_text[:raw_text.find("[[SEND_MAIL:")].strip() + f"\n\n({send_result})"
                else:
                    response_text = "HATA: Mail formatı yanlış. [[SEND_MAIL: Alıcı | Konu | Mesaj]]"

            elif "[[GOOGLE_SEND_MAIL:" in raw_text:
                # Eski Google API Yöntemi (Yedek)
                start = raw_text.find("[[GOOGLE_SEND_MAIL:") + len("[[GOOGLE_SEND_MAIL:")
                end = raw_text.find("]]", start)
                params = raw_text[start:end].split("|")
                if len(params) >= 3:
                    to_email = params[0].strip()
                    subject = params[1].strip()
                    body = params[2].strip()
                    send_result = tools_google.send_email(to_email, subject, body)
                    response_text = raw_text[:raw_text.find("[[GOOGLE_SEND_MAIL:")].strip() + f"\n({send_result})"
                else:
                    response_text = "HATA: Mail formatı yanlış. (Alici | Konu | Mesaj)"

            elif "[[WEATHER:" in raw_text:
                start = raw_text.find("[[WEATHER:") + len("[[WEATHER:")
                end = raw_text.find("]]", start)
                city = raw_text[start:end].strip()
                if not city: city = "Istanbul"
                
                weather_info = weather.weather_service.get_weather(city)
                system_log = f"Hava Durumu: {city}"
                
                # Hava durumunu kullanıcıya okuyacak metne dönüştür
                response_text = raw_text.replace(f"[[WEATHER:{city}]]", "").strip()
                if not response_text: response_text = "Hava durumu verisi alindi."
                response_text += f"\n\n🌤️ {weather_info}"
                
            elif "[[OPEN_BLACKBOX]]" in raw_text:
                action = "open_blackbox"
                response_text = raw_text.replace("[[OPEN_BLACKBOX]]", "").strip()
            
            elif "[[OPEN_APP:" in raw_text:
                start = raw_text.find("[[OPEN_APP:") + len("[[OPEN_APP:")
                end = raw_text.find("]]", start)
                app_name = raw_text[start:end].strip()
                
                tool_result = tools_pc.open_application(app_name)
                system_log = f"Uygulama: {tool_result}"
                response_text = raw_text[:raw_text.find("[[OPEN_APP:")].strip() + f"\n({tool_result})"

            elif "[[READ_FILES:" in raw_text:
                start = raw_text.find("[[READ_FILES:") + len("[[READ_FILES:")
                end = raw_text.find("]]", start)
                location = raw_text[start:end].strip()
                
                tool_result = tools_pc.list_user_files(location)
                system_log = f"Dosya Okuma: {location}"
                response_text = raw_text[:raw_text.find("[[READ_FILES:")].strip() + f"\n\n📂 DOSYALAR:\n{tool_result}"
                
            elif "[[CMD:" in raw_text:
                start = raw_text.find("[[CMD:") + len("[[CMD:")
                end = raw_text.find("]]", start)
                cmd_content = raw_text[start:end]
                parts = cmd_content.split("|")
                if len(parts) >= 2:
                    license_key = parts[0].strip()
                    cmd_name = parts[1].strip()
                    cmd_args = parts[2].strip() if len(parts) > 2 else "{}"
                    
                    # Action format: client_command:KEY:CMD:ARGS
                    action = f"client_command:{license_key}:{cmd_name}:{cmd_args}"
                    system_log = f"Komut: {cmd_name} -> {license_key}"
                    response_text = raw_text.replace(f"[[CMD:{cmd_content}]]", "").strip() 
                    if not response_text: response_text = f"Komut iletildi: {cmd_name} ({license_key})"
                else:
                     response_text = "HATA: Komut formatı yanlış. (Lisans | Komut | Arg)"

            elif "[[SEND_PRESENTATION:" in raw_text:
                start = raw_text.find("[[SEND_PRESENTATION:") + len("[[SEND_PRESENTATION:")
                end = raw_text.find("]]", start)
                params = raw_text[start:end].split("|")
                # Format: [[SEND_PRESENTATION: product_key | email]]
                if len(params) >= 2:
                    prod_key = params[0].strip().lower() # stock, crm, staff
                    target_email = params[1].strip()
                    
                    # Eşleşme bul (stok -> stock, emlak -> crm vb.)
                    key_map = {
                        "stok": "stock", "stock": "stock",
                        "emlak": "crm", "crm": "crm", "city": "crm",
                        "staff": "staff", "personel": "staff",
                        "yatırım": "invest", "invest": "invest"
                    }
                    mapped_key = key_map.get(prod_key, "stock") # Varsayılan stock
                    
                    data = marketing.get_presentation_content(mapped_key)
                    
                    if data:
                        # TOPLU GÖNDERİM MODU
                        if target_email.lower() in ["tümü", "tumu", "all", "hepsi", "leads"]:
                            pending_leads = db.query(models.Lead).filter(models.Lead.status == "new").limit(5).all() # Güvenlik için batch 5
                            
                            if not pending_leads:
                                response_text = "Henüz gönderim yapılmamış (yeni) potansiyel müşteri bulunmuyor. Önce 'Müşteri Avcısı'nı çalıştırın."
                            else:
                                success_count = 0
                                sent_addresses = []
                                
                                for lead in pending_leads:
                                    try:
                                        # Özelleştirme (Varsa)
                                        custom_body = data["body"] # İleride lead.name varsa eklenebilir
                                        
                                        res = tools_smtp.send_email_smtp(
                                            lead.email,
                                            data["subject"],
                                            custom_body,
                                            attachment_paths=data["attachments"]
                                        )
                                        
                                        if "başarıyla" in res:
                                            lead.status = "contacted"
                                            lead.last_contacted = datetime.datetime.utcnow()
                                            success_count += 1
                                            sent_addresses.append(lead.email)
                                            # Rate limit zaten tools_smtp içinde var ama burada da kısa bir 'düşünme' payı
                                            # time.sleep(1) # Gerek yok, func içinde bloklanıyor
                                    except Exception as e:
                                        print(f"BULK MAIL ERROR: {e}")
                                
                                db.commit()
                                response_text = f"📢 **Toplu Gönderim Başladı**\n\n{len(pending_leads)} adaydan {success_count} tanesine başarılı şekilde sunum yollandı.\n\nGönderilenler:\n- " + "\n- ".join(sent_addresses)
                                if len(pending_leads) < 5:
                                    response_text += "\n\n(Kota/Hız limiti nedeniyle 5'erli paketler halinde gönderiyorum)"

                        else:
                            # TEKİL GÖNDERİM (ESKİ YÖNTEM)
                            system_log = f"Sunum Gönderiliyor: {mapped_key} -> {target_email}"
                            send_res = tools_smtp.send_email_smtp(
                                target_email, 
                                data["subject"], 
                                data["body"], 
                                attachment_paths=data["attachments"]
                            )
                            response_text = raw_text[:raw_text.find("[[SEND_PRESENTATION:")].strip() + f"\n\n✅ {data['product_name']} sunumu gönderildi.\n({send_res})"
                    else:
                        response_text = "HATA: Sunum verisi bulunamadı."
                else:
                    response_text = "HATA: Format yanlış. [[SEND_PRESENTATION: ürün | mail]]"

            elif "[[FIND_LEADS:" in raw_text:
                start = raw_text.find("[[FIND_LEADS:") + len("[[FIND_LEADS:")
                end = raw_text.find("]]", start)
                sector_arg = raw_text[start:end].strip().lower()
                
                # Sektör eşleştirmesi
                if "tümü" in sector_arg or "hepsi" in sector_arg or "all" in sector_arg: target_sector = "all"
                elif "kafe" in sector_arg or "cafe" in sector_arg: target_sector = "cafe"
                elif "restoran" in sector_arg or "yemek" in sector_arg: target_sector = "restaurant"
                elif "emlak" in sector_arg: target_sector = "real_estate"
                elif "market" in sector_arg or "perakende" in sector_arg: target_sector = "retail"
                elif "kurumsal" in sector_arg or "holding" in sector_arg: target_sector = "corporate"
                else: target_sector = "all" # Varsayılan olarak hepsini tarasın (Kullanıcı 'avla' dediğinde)
                
                system_log = f"Müşteri Avı Başlatıldı: {target_sector.upper()}"
                
                system_log = f"Müşteri Avı Başlatıldı: {target_sector}"
                
                # Senkron olarak çalıştırıyoruz (Blocking olabilir, thread gerekebilir ama şimdilik basit)
                try:
                    leads = lead_hunter.hunter_service.search_leads(db, target_sector)
                    count = len(leads)
                    response_text = raw_text[:raw_text.find("[[FIND_LEADS:")].strip() + f"\n\n🎯 **AVLANMA SONUCU**\n\nİnternetin derinliklerinden **{count} adet** potansiyel müşteri e-postası yakaladım.\n\nBulunan Bazı Adresler:\n- " + "\n- ".join(leads[:5])
                    if count > 5: response_text += f"\n...ve {count-5} tane daha."
                    
                    response_text += "\n\nBu adreslere sunum göndermek için: `[[SEND_PRESENTATION: stock | tumu]]` henüz aktif değil, tek tek gönderebilirsiniz."
                except Exception as e:
                    response_text = f"HATA: Müşteri avı sırasında sorun oluştu: {str(e)}"

            elif "[[ANALYSIS]]" in raw_text:
                system_log = "Analiz Raporu Oluşturuluyor..."
                report = analysis.analysis_service.generate_brief_for_azi(db)
                response_text = raw_text.replace("[[ANALYSIS]]", "").strip()
                response_text += f"\n\n📊 SİSTEM ANALİZİ:\n{report}"

            elif "[[LEARN:" in raw_text:
                start = raw_text.find("[[LEARN:") + len("[[LEARN:")
                end = raw_text.find("]]", start)
                info = raw_text[start:end].strip()
                
                # Bilgiyi 'fact' olarak kaydet
                fact_mem = models.AIMemory(
                    memory_type="fact",
                    content=info,
                    timestamp=datetime.datetime.utcnow()
                )
                db.add(fact_mem)
                
                system_log = f"Bilgi Öğrenildi: {info}"
                response_text = raw_text.replace(f"[[LEARN:{info}]]", "").strip()
                if not response_text: response_text = "Bunu hafızama kaydettim Alpay Bey."

                if not response_text: response_text = "Bunu hafızama kaydettim Alpay Bey."

            elif "[[PUSH_NOTIFICATION:" in raw_text:
                start = raw_text.find("[[PUSH_NOTIFICATION:") + len("[[PUSH_NOTIFICATION:")
                end = raw_text.find("]]", start)
                content = raw_text[start:end]
                params = content.split("|")
                
                if len(params) >= 2:
                    title = params[0].strip()
                    msg = params[1].strip()
                    
                    # Async gönder (Main thread'de olduğumuz için ensure_future veya run_until_complete gerekebilir ama
                    # notifier.send_async zaten loop'a atıyor)
                    import asyncio
                    try:
                        # Mevcut loop'u bulmaya çalış
                        loop = asyncio.get_event_loop()
                        loop.create_task(notifier.send_async(title, msg, priority=3))
                    except:
                        # Loop yoksa senkron dene (nadir durum)
                        notifier.send(title, msg, priority=3)
                        
                    system_log = f"Bildirim Gönderildi: {title}"
                    response_text = raw_text.replace(f"[[PUSH_NOTIFICATION:{content}]]", "").strip()
                    if not response_text: response_text = "Rapor telefonunuza iletildi Alpay Bey."
                    response_text += "\n(Bildirim Gönderildi 📲)"
                else:
                    response_text = "HATA: Bildirim formatı yanlış."

            else:
                response_text = raw_text

        except Exception as e:
            error_msg = str(e)
            print(f"BEYİN HATASI: {error_msg}")
            
            # --- OFFLINE REFLEX ---
            # Eğer hata Google/Network hatasıysa veya 429 ise Refleks devreye girsin
            print("Refleks Modu Devreye Giriyor...")
            reflex_response = self._local_reflex(text, db)
            response_text = reflex_response

        # --- LABEL KONTROL (Tekrar kontrol et, çünkü Refleks [[CMD]] döndürebilir) ---
        # Refleks sonucu raw_text gibi işlenmeli
        if response_text.startswith("[[") and response_text.endswith("]]"):
             raw_text = response_text # Refleks bir komut döndü
             # Burayı tekrar işlemek için recursive çağırabiliriz veya kod tekrarı yapabiliriz.
             # Basitlik adına Process akışını yeniden düzenlemek daha doğru ama şimdilik
             # Refleks sadece ANALYSIS döndürüyor, aşağıda ANALYSIS handler var zaten.
             pass

        # 2. Cevabı Kaydet
        azi_memory = models.AIMemory(
            memory_type="azi_response",
            content=response_text,
            timestamp=datetime.datetime.utcnow()
        )
        db.add(azi_memory)
        
        if system_log:
             db.add(models.AIMemory(memory_type="system_log", content=system_log, timestamp=datetime.datetime.utcnow()))
             
        db.commit()

        return {"text": response_text, "action": action}

# --- UNUTULAN PARÇA GARANTİSİ ---
brain_service = AZIBrain()
