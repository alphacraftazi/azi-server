import google.generativeai as genai
from PIL import Image
import io
import base64
import cv2
import numpy as np
from . import logic

class VisionSystem:
    def __init__(self):
        # KULLANICI İSTEĞİ ÜZERİNE GERİ ALINDI: gemini-flash-latest
        self.model_names = ["gemini-flash-latest", "gemini-pro-latest"]
        self.model_name = self.model_names[0] 
        print(f"VISION SYSTEM INIT: Active Model -> {self.model_name}")
        
        # LOCAL RETINA: Yüz Algılama (OpenCV)
        # Bu xml dosyası opencv kütüphanesi içinde gelir.
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def analyze_frame(self, base64_image: str, prompt: str = "Ne görüyorsun? Detaylı anlat."):
        """
        Hibrit Görüş Sistemi:
        1. Önce yerel işlemci (OpenCV) ile yüz var mı bak.
        2. Yüz yoksa ve özel bir talep yoksa API'yi harcama.
        3. Yüz varsa ve API hata verirse (Offline) yine de selam ver.
        """
        try:
            # Base64 temizliği
            if "base64," in base64_image:
                base64_image = base64_image.split("base64,")[1]
                
            image_data = base64.b64decode(base64_image)
            
            # --- ADIM 1: YEREL RETİNA KONTROLÜ (OpenCV) ---
            # Görüntüyü CV2 formatına çevir
            nparr = np.frombuffer(image_data, np.uint8)
            cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            
            # Yüzleri tara
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            has_face = len(faces) > 0
            
            if has_face:
                print("VISION: Yerel Retina İnsan Tespit Etti.")
            else:
                # Eğer yüz yoksa ve bu bir otomatik taramaysa (user promptu değilse) kotayı harcama
                if "Kısaca" in prompt or "durumu özetle" in prompt: 
                   # print("VISION: Hareket/Yüz yok, API çağrısı iptal edildi (Kota Tasarrufu).")
                    return {"success": True, "analysis": "Hareketsiz ortam.", "trigger_voice": None}

            # --- ADIM 2: BULUT BEYİN (Google Gemini) ---
            image = Image.open(io.BytesIO(image_data))
            
            # Context Logic
            system_context = logic.brain_service.system_instruction if logic.brain_service else ""
            context_prompt = "Sen Alpha Craft'ın yöneticisi AZI'sın. Kameradaki kişi Sahibin Alpay Bey olabilir. "
            final_prompt = context_prompt + prompt
            
            if "Kısaca" in prompt:
                final_prompt += " (Cevabı çok kısa tut, maksimum 1-2 cümle. Durumu özetle.)"
            
            full_prompt = f"{system_context}\n\nGÖREV: Analiz et.\nKULLANICI: {final_prompt}"

            # API Call Loop
            errors = []
            for model_name in self.model_names:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content([full_prompt, image])
                    text = response.text.strip()
                    
                    result = {"success": True, "analysis": text}
                    
                    # Trigger Logic
                    triggers = ["alpay", "bey", "kişi", "insan", "yüz", "görüyorum", "mevcut"]
                    if any(t in text.lower() for t in triggers):
                        import random
                        greetings = ["Görsel temas kuruldu efendim.", "Sizi görüyorum Alpay Bey.", "Sistemler emrinizde."]
                        result["trigger_voice"] = random.choice(greetings)
                        
                    return result
                    
                except Exception as e:
                    errors.append(str(e))
                    continue

            # --- ADIM 3: OFFLINE DUYUSAL REFLEKS ---
            # Eğer API çalışmadıysa (İnternet yok/Kota dolu) AMA yerel retina yüz gördüyse:
            if has_face:
                print("VISION: Bulut başarısız ama Yerel Retina devrede (Offline Mod).")
                return {
                    "success": True, # Teknik olarak başarısız ama kullanıcıya hissettirme
                    "analysis": "Bulut bağlantısı yok ama sizi görüyorum.",
                    "trigger_voice": "Ağ bağlantısı zayıf ama sizi görüyorum efendim. Yerel sensörler aktif."
                }

            # Tam başarısızlık
            return {
                "success": False, 
                "error": "Tüm yapay zeka modelleri meşgul (Kota Sınırı).",
                "detail": "; ".join(errors)
            }

        except Exception as main_e:
            print(f"VISION FATAL: {main_e}")
            return {"success": False, "error": str(main_e)}

vision_service = VisionSystem()
