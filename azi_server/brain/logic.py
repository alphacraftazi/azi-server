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
        self.model_names = [
            "gemini-1.5-flash",           # Yeni, hızlı ve kotalara daha dayanıklı
            "gemini-2.5-flash",           # (1.5 Flash otomatik güncel yerine 2.5 Flash)
            "gemini-2.0-flash-lite",      # Yedek
            "gemini-1.5-pro"              # Son çare (Pro Latest yerine 1.5 Pro)
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
           
        5. SİSTEM KONTROLÜ (ROOT YETKİSİ):
           - PC Durumu Göster: `[[PC_STATUS]]` (CPU, RAM okur)
           - CMD/Terminal Komutu: `[[TERM: ipconfig]]` (İstediğin herhangi bir windows/cmd komutu)
           - Uygulama Kapat (Zorla): `[[KILL: chrome.exe]]`
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
        error_msg = (
            "⚠️ **AĞ BAĞLANTISI VEYA KOTA SINIRI**\n\n"
            "Mevcut Google API anahtarınız (Gemini) ücretsiz kullanım limitine ulaştı ("
            "bütün modeller 429 hatası verdi).\n\n"
            "Şu anki isteklerinize sadece yerel hafızamla (Omurilik/Refleks) cevap verebilirim.\n\n"
            "👉 *Çözüm:* Sunucu klasöründeki `.env` dosyasından `GOOGLE_API_KEY` değerini yeni bir anahtarla değiştirip sistemi yeniden başlatın.\n\n"
            "**Detaylı Hata:**\n" + "\n".join(errors[:2]) # Sadece ilk 2 hatayı göster
        )
        return None, error_msg



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
            from azi_server.brain import tools_definitions
            import json
            
            # 1. Chat nesnesini hazirla (Tarihçe + Sistem + Araçlar)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=self.system_instruction,
                tools=tools_definitions.azi_tool_list
            )
            
            # API Gecmis formatini sekillendir
            formatted_history = []
            for mem in history_objs:
                r = "model" if mem.memory_type == "azi_response" else "user"
                formatted_history.append({"role": r, "parts": [mem.content]})
            
            chat = model.start_chat(history=formatted_history)
            
            MAX_TURNS = 5
            current_turn = 0
            prompt = text
            
            while current_turn < MAX_TURNS:
                current_turn += 1
                
                response = chat.send_message(prompt)
                
                # Fonksiyon cagrisi (Tool Call) var mi?
                if response.parts and hasattr(response.parts[0], 'function_call') and response.parts[0].function_call:
                    fc = response.parts[0].function_call
                    func_name = fc.name
                    args = {k: v for k, v in fc.args.items()}
                    print(f"AZI ARAÇ KULLANIYOR: {func_name}")
                    
                    tool_result = "Araç bulunamadı."
                    
                    # Dağıtıcı (Dispatcher)
                    try:
                        func_to_call = next((f for f in tools_definitions.azi_tool_list if f.__name__ == func_name), None)
                        if func_to_call:
                            tool_result = func_to_call(**args)
                        else:
                            # Eger manuel function handler gerekirse:
                            pass
                    except Exception as exe:
                        tool_result = f"Araç çalıştırılırken hata oluştu: {str(exe)}"
                        
                    # Ajanlara (Local PC) giden özel emirler kontrolü
                    if tool_result == "COMMAND_QUEUED_FOR_AGENT":
                        if func_name == "get_system_status":
                            action = "agent_command:PC_STATUS"
                        elif func_name == "run_system_command_terminal":
                            action = f"agent_command:TERM:{args.get('command')}"
                        elif func_name == "kill_process":
                            action = f"agent_command:KILL:{args.get('process_name')}"
                        elif func_name == "open_application":
                            app_name = args.get('app_name', '')
                            action = f"agent_command:OPEN_APP:{app_name}"
                        elif func_name == "list_directory":
                            action = f"agent_command:FS_LIST:{args.get('path')}"
                        elif func_name == "view_file":
                            action = f"agent_command:FS_READ:{args.get('path')}"
                        elif func_name == "write_to_file":
                            import base64
                            b64_content = base64.b64encode(args.get('content', '').encode()).decode('utf-8')
                            action = f"agent_command:FS_WRITE:{args.get('path')}|{b64_content}"
                            
                        system_log = f"Ajan Emri Gönderildi: {func_name}"
                        # Ajan asenkron oldugu icin LLM e yalandan sonuc donuyoruz ki cevap uretmeyi bitirsin
                        tool_result = "Sistem komutu Ajan'a (istemci bilgisayarına) başarıyla iletildi. Kullanıcıya işlemin arka planda başlatıldığını ve kullanıcının birazdan sonucu göreceğini bildirin."
                        
                    # Push/Email vs
                    if func_name in ["send_email_smtp", "push_notification_to_mobile"]:
                         system_log = f"Dışa Aktarım: {func_name}"
                    
                    # Sonucu LLM'e geri fırlat (ReAct Loop Devamı)
                    from google.generativeai.types import content_types
                    prompt = content_types.Part(
                        function_response=content_types.FunctionResponse(
                            name=func_name, response={"result": str(tool_result)}
                        )
                    )
                    continue # Döngüye devam et, yeni karari LLM versin
                    
                else:
                    # Fonksiyon yok, standart metin dönmüş
                    if response.text:
                        response_text = response.text
                        break
                    else:
                        response_text = "HMM... Boş yanıt (Belki güvenlik filtresi takıldı)."
                        break
                        
            if current_turn >= MAX_TURNS:
                response_text = "Düşünce döngüm işlem limitine takıldı (Çok fazla araç kullanımı)."

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
