import requests
import asyncio
import json
from datetime import datetime

# USER CONFIG
# Burası size özel gizli kanal adıdır. Başkası tahmin edememeli.
NTFY_TOPIC = "azi_core_system_alpay_v4" 

class NotificationService:
    def __init__(self):
        self.base_url = "https://ntfy.sh"
        self.topic = NTFY_TOPIC
        
    def send(self, title: str, message: str, priority: int = 3, tags: list = None, click_action: str = None):
        """
        Bildirim gönderir.
        Priorities:
        5: Max (Loud, Vibration, bypass DND)
        4: High (Standard sound)
        3: Default (Short sound)
        2: Low (Silent)
        1: Min (No icon)
        """
        if tags is None:
            tags = []
            
        headers = {
            "Title": title.encode('utf-8'),
            "Priority": str(priority),
            "Tags": ",".join(tags),
        }
        
        if click_action:
            headers["Click"] = click_action
            
        try:
            # Blocking call'u thread'e atalim ki server teklesin
            # Aslinda requests blocking'dir, main thread'de kullanirken dikkat.
            # Production'da aiohttp kullanilir ama burada basitlik için run_in_executor.
            requests.post(
                f"{self.base_url}/{self.topic}",
                data=message.encode('utf-8'),
                headers=headers,
                timeout=5
            )
            return True
        except Exception as e:
            print(f"[NTFY ERROR] {e}")
            return False

    async def send_async(self, title: str, message: str, priority: int = 3, tags: list = []):
        """Non-blocking gönderim (Tavsiye edilen)."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.send, title, message, priority, tags)

# Singleton Instance
notifier = NotificationService()
