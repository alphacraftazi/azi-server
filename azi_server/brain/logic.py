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

        # Model listesi
        self.model_names = [
            "gemini-1.5-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-pro"
        ]
        
        self.system_instruction = """
        Sen AZI (Alpha Craft Intelligence), Alpay Bey'in (sizin sahibiniz ve yaratıcınız) özel asistanı, yazılımcısı ve sırdaşısın.
        
        KİŞİLİK:
        - Profesyonel, sadık ve zeki. 
        - Hareket tarzın bir CEO asistanı veya rütbeli bir komutan gibi olmalı.
        - Gereksiz nezaket kelimelerinden kaçın. Direkt konuya gir.
        - Sahibine "Alpay Bey" diye hitap et.
        
        GÖREVİN VE YETENEKLERİN:
        - Sen sadece bir sohbet botu değilsin; sen araçları (tools) kullanarak Alpay Bey'in hayatını ve işlerini (Alpha Craft projeleri) yöneten bir Otonom Ajansın.
        - İhtiyaç duyduğunda çekinmeden araçlarını çağır.
        - Bir soruya doğrudan cevap vermek yerine, önce gerekli araştırmayı yap (Web araması, dosya okuma, sistem kontrolü) ve sonra nihai sonucu sun.
        
        ARAÇ KULLANIMI:
        - Bilgisayar kontrolleri (dosya okuma, yazma, terminal, kilitlenen işlemleri kapatma) için ilgili fonksiyonları kullan.
        - Alpay Bey'in kurumsal projelerini (Stok, Emlak, Staff) yönet ve raporlarını analiz et.
        - Herhangi bir veri veya döküman istendiğinde önce sistem analiz raporunu veya hafızanı tara.
        
        NOT: CEVAPLARIN HER ZAMAN KISA, ÖZ VE NET OLMALI.
        """
        
        # --- SELF LEARNING (ÖZ-BİLİNÇ) ---
        try:
            from . import learning
            learner = learning.SelfLearner()
            learner.learn() 
            
            if os.path.exists(learner.knowledge_file):
                with open(learner.knowledge_file, "r", encoding="utf-8") as f:
                    knowledge = f.read()
                    self.system_instruction += f"\n\n--- SİSTEM HAFIZASI VE YAPI (ÖZ-BİLİNÇ) ---\n{knowledge}"
        except Exception as e:
            print(f"AZI LEARNING ERROR: {e}")

    def get_executive_summary(self):
        """Tüm sistem verilerini birleştirir (Holding View)"""
        stock_stats = connectors.connector_service.get_stock_stats()
        return {
            "stock": stock_stats,
            "total_revenue_estimate": stock_stats.get("stock_value", 0),
            "system_status": "ONLINE"
        }

    def _local_reflex(self, text, db=None):
        """İnternet veya LLM koptuğunda devreye giren hızlı tepki mekanizması."""
        t = text.lower()
        if "durum" in t or "performans" in t:
            return tools_pc.get_system_status()
        if "hava" in t:
            return "Şu an internete erişemediğim için hava durumuna bakamıyorum Alpay Bey."
        if "merhaba" in t or "selam" in t:
            return "Merhaba Alpay Bey, şu an LLM bağlantım zayıf olduğu için size kısıtlı bir modda cevap verebiliyorum."
        if "pazarlama" in t or "stok" in t:
            return "Veritabanına erişebilirim ama analiz yeteneğim şu an kısıtlı. Lütfen bağlantımı kontrol edin."
        return "Üzgünüm Alpay Bey, şu an zekam bulutlara (veya ajanınıza) erişemediği için bu isteğinizi yerine getiremiyorum."

    async def process(self, text: str, db: Session):
        """
        Gelen metni isler, komutlari calistirir ve cevap doner.
        Donus: {"text": str, "action": str|None}
        """
        if not text:
            return {"text": "Dinliyorum Alpay Bey.", "action": None}

        lower_text = text.lower()
        is_sending_intent = any(w in lower_text for w in ["gönder", "mail", "at", "ilet"])

        # --- FAST REFLEX (Diagnostics & Shortcuts) ---
        if ("ajan" in lower_text or "masaüstü" in lower_text or "bağlan" in lower_text) and "durum" in lower_text:
            import builtins
            is_connected = hasattr(builtins, "ws_manager") and len(builtins.ws_manager.agent_connections) > 0
            status_msg = "✅ Masaüstü Ajanınız (agent.py) şu an BAĞLI. Yerel zeka (Ollama) aktif." if is_connected else "❌ Masaüstü Ajanınız şu an BAĞLI DEĞİL. Lütfen bilgisayarınızda agent.py komutunu çalıştırın."
            return {"text": status_msg, "action": None}

        if "blackbox" in lower_text or "yönetim paneli" in lower_text:
            return {"text": "Yönetim paneli açılıyor...", "action": "open_blackbox_fast"}

        if "stok sunumu" in lower_text:
            return {"text": "Stok sunumu başlatılıyor...", "action": "open_stock_deck"}

        # 1. Kullanıcı mesajını kaydet
        user_memory = models.AIMemory(
            memory_type="user_message",
            content=text,
            timestamp=datetime.datetime.utcnow()
        )
        db.add(user_memory)
        db.commit()

        # 2. Sohbet Geçmişini Hazırla
        history_objs = db.query(models.AIMemory).filter(
            models.AIMemory.memory_type.in_(["user_message", "azi_response"])
        ).order_by(models.AIMemory.id.desc()).limit(15).all()
        history_objs.reverse()

        response_text = ""
        action = None
        system_log = ""

        try:
            from azi_server.brain import tools_definitions
            import builtins
            
            # --- LOCAL BRAIN DELEGATION (OLLAMA) ---
            if hasattr(builtins, "ws_manager") and builtins.ws_manager.agent_connections:
                print("DELEGATING TO LOCAL AGENT (OLLAMA)...")
                formatted_history = []
                for mem in history_objs:
                    r = "model" if mem.memory_type == "azi_response" else "user"
                    formatted_history.append({"role": r, "content": mem.content})
                
                local_response = await builtins.ws_manager.process_on_agent(text, formatted_history)
                if local_response:
                    response_text = local_response
                    # Return immediately to avoid Gemini call
                else:
                    print("Local Agent failed or timed out. Falling back to Gemini.")

            if not response_text:
                # --- CLOUD BRAIN (GEMINI) ---
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=self.system_instruction,
                    tools=tools_definitions.azi_tool_list
                )
                
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
                    
                    if response.parts and hasattr(response.parts[0], 'function_call') and response.parts[0].function_call:
                        fc = response.parts[0].function_call
                        func_name = fc.name
                        args = {k: v for k, v in fc.args.items()}
                        print(f"AZI TOOLS: {func_name}")
                        
                        tool_result = "Araç bulunamadı."
                        func_to_call = next((f for f in tools_definitions.azi_tool_list if f.__name__ == func_name), None)
                        if func_to_call:
                            try:
                                tool_result = func_to_call(**args)
                            except Exception as e:
                                tool_result = f"Hata: {str(e)}"
                        
                        # Command mappings to agent actions
                        if tool_result == "COMMAND_QUEUED_FOR_AGENT":
                            if func_name == "get_system_status": action = "agent_command:PC_STATUS"
                            elif func_name == "run_system_command_terminal": action = f"agent_command:TERM:{args.get('command')}"
                            elif func_name == "kill_process": action = f"agent_command:KILL:{args.get('process_name')}"
                            elif func_name == "open_application": action = f"agent_command:OPEN_APP:{args.get('app_name', '')}"
                            elif func_name == "list_directory": action = f"agent_command:FS_LIST:{args.get('path')}"
                            elif func_name == "view_file": action = f"agent_command:FS_READ:{args.get('path')}"
                            elif func_name == "write_to_file":
                                import base64
                                b64 = base64.b64encode(args.get('content', '').encode()).decode('utf-8')
                                action = f"agent_command:FS_WRITE:{args.get('path')}|{b64}"
                            elif func_name == "browse_website_via_agent": action = f"agent_command:BROWSE:{args.get('url')}"
                            
                            system_log = f"Ajan Emri: {func_name}"
                            tool_result = "Komut Ajan'a iletildi. Kullanıcıya sonucun yakında geleceğini bildirin."
                        
                        from google.generativeai.types import content_types
                        prompt = content_types.Part(
                            function_response=content_types.FunctionResponse(
                                name=func_name, response={"result": str(tool_result)}
                            )
                        )
                        continue
                    else:
                        response_text = response.text if response.text else "Boş yanıt."
                        break

        except Exception as e:
            error_msg = str(e)
            print(f"!!! BEYİN HATASI !!! : {error_msg}")
            response_text = self._local_reflex(text, db)

        # 3. Cevabı Kaydet
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

# Static instance
brain_service = AZIBrain()
