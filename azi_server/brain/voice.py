import edge_tts
import asyncio
import os
import hashlib

class VoiceManager:
    """
    Microsoft Edge Neural TTS (edge-tts) kullanarak yüksek kaliteli ses dosyaları oluşturur.
    """
    def __init__(self):
        # Ses dosyalarının kaydedileceği klasör
        # Production ortamı için güvenli yol belirleme:
        # Bu dosya: azi_server/brain/voice.py
        # Hedef: azi_app/audio_cache
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.cache_dir = os.path.join(base_dir, "azi_app", "audio_cache")
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        # Model Ayarları
        self.voice = "tr-TR-AhmetNeural" # Daha tok ve karizmatik erkek sesi
        self.rate = "+10%" # Biraz daha canlı ve hızlı

    def _generate_file_hash(self, text):
        return hashlib.md5(f"{text}-{self.voice}-{self.rate}".encode('utf-8')).hexdigest()

    async def _create_audio_file(self, text, file_path):
        """Async olarak sesi oluşturur"""
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
        await communicate.save(file_path)

    async def generate_audio(self, text):
        """
        Async wrapper.
        """
        try:
            filename = f"{self._generate_file_hash(text)}.mp3"
            file_path = os.path.join(self.cache_dir, filename)
            
            if os.path.exists(file_path):
                return f"/audio_cache/{filename}"
            
            # Async call directly
            await self._create_audio_file(text, file_path)
            return f"/audio_cache/{filename}"
            
        except Exception as e:
            print(f"Neural Voice Error: {e}")
            return None

voice_service = VoiceManager()
