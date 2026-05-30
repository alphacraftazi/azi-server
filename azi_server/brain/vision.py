import google.generativeai as genai
from PIL import Image
import io
import base64
import cv2
import numpy as np
import os
from . import logic

class VisionSystem:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        self.model_names = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.0-flash-lite"]
        self.model_name = self.model_names[0]
        print(f"VISION SYSTEM INIT: Active Model -> {self.model_name}")
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def analyze_frame(self, base64_image: str, prompt: str = "Ne görüyorsun? Detaylı anlat."):
        try:
            if "base64," in base64_image:
                base64_image = base64_image.split("base64,")[1]
            image_data = base64.b64decode(base64_image)

            nparr = np.frombuffer(image_data, np.uint8)
            cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            has_face = len(faces) > 0

            if has_face:
                print("VISION: Yerel Retina İnsan Tespit Etti.")
            else:
                if "Kısaca" in prompt or "durumu özetle" in prompt:
                    return {"success": True, "analysis": "Hareketsiz ortam.", "trigger_voice": None}

            image = Image.open(io.BytesIO(image_data))
            system_context = logic.brain_service.system_instruction if logic.brain_service else ""
            context_prompt = "Sen Alpha Craft'ın yöneticisi AZI'sın. Kameradaki kişi Sahibin Alpay Bey olabilir. "
            final_prompt = context_prompt + prompt
            if "Kısaca" in prompt:
                final_prompt += " (Cevabı çok kısa tut, maksimum 1-2 cümle.)"
            full_prompt = f"{system_context}\n\nGÖREV: Analiz et.\nKULLANICI: {final_prompt}"

            errors = []
            for model_name in self.model_names:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content([full_prompt, image])
                    text = response.text.strip()
                    result = {"success": True, "analysis": text}
                    triggers = ["alpay", "bey", "kişi", "insan", "yüz", "görüyorum", "mevcut"]
                    if any(t in text.lower() for t in triggers):
                        import random
                        greetings = ["Görsel temas kuruldu efendim.", "Sizi görüyorum Alpay Bey.", "Sistemler emrinizde."]
                        result["trigger_voice"] = random.choice(greetings)
                    return result
                except Exception as e:
                    errors.append(str(e))
                    continue

            if has_face:
                return {"success": True, "analysis": "Bulut bağlantısı yok ama sizi görüyorum.", "trigger_voice": "Ağ bağlantısı zayıf ama sizi görüyorum efendim."}

            return {"success": False, "error": "Tüm modeller meşgul.", "detail": "; ".join(errors)}

        except Exception as main_e:
            print(f"VISION FATAL: {main_e}")
            return {"success": False, "error": str(main_e)}

vision_service = VisionSystem()
