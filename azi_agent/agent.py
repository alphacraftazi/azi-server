import sys
import os
import json
import asyncio
import websockets
import requests

# Proje kök dizinini Python yoluna ekle ki tools_pc.py kütüphanesini içeri aktarabilelim
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from azi_server.brain import tools_pc

# --- CONFIG ---
URI = "wss://azi-server.onrender.com/ws/agent"
OLLAMA_URL = "http://localhost:11434/api/chat"
LOCAL_MODEL = "llama3" # Llama3, Mistral, Gemma2 vb. (Ollama'da yüklü olmalı)

SYSTEM_PROMPT = """Sen AZI (Alpha Craft Intelligence) yapay zekasısın. Alpay Bey'in özel dijital asistanısın. 
Şu an bulut (Render) üzerinden gelen talepleri yerel bilgisayarda (Edge) işliyorsun. 
Cevapların kısa, öz ve profesyonel olmalı. Alpay Bey'e 'Efendim' veya 'Alpay Bey' diye hitap et.
Sistem kontrolleri ve dosya işlemleri yetkin var."""

import aiohttp

async def call_local_llm(prompt, history=[]):
    """Ollama üzerinden yerel LLM'i çalıştırır."""
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in history:
            messages.append(h)
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": LOCAL_MODEL,
            "messages": messages,
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_URL, json=payload, timeout=60) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("message", {}).get("content", "Bir hata oluştu.")
                else:
                    return f"Ollama Hatası: {response.status}. Lütfen Ollama'nın çalıştığından emin olun."
    except Exception as e:
        return f"Yerel Zeka Bağlantı Hatası: {str(e)}. (Ollama servisiniz açık mı?)"

def execute_local_tool(command):
    """Master'dan gelen veya yerel LLM'in istediği araçları çalıştırır."""
    if command == "PC_STATUS":
        return tools_pc.get_system_status()
    elif command.startswith("TERM:"):
        return tools_pc.run_system_command(command.replace("TERM:", "", 1))
    elif command.startswith("KILL:"):
        return tools_pc.kill_process(command.replace("KILL:", "", 1))
    elif command.startswith("FS_LIST:"):
        path = command.replace("FS_LIST:", "", 1)
        try:
            target_path = os.getcwd() if path == "." else path
            items = os.listdir(target_path)
            return f"Klasör ({target_path}):\n" + "\n".join(items[:100])
        except Exception as e: return f"Hata: {e}"
    elif command.startswith("FS_READ:"):
        path = command.replace("FS_READ:", "", 1)
        try:
            with open(path, "r", encoding="utf-8") as f: return f.read(5000)
        except Exception as e: return f"Hata: {e}"
    elif command.startswith("FS_WRITE:"):
        parts = command.replace("FS_WRITE:", "", 1).split("|", 1)
        if len(parts) == 2:
            import base64
            path, b64_content = parts[0], parts[1]
            content = base64.b64decode(b64_content).decode("utf-8")
            try:
                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f: f.write(content)
                return f"Başarılı: {path}"
            except Exception as e: return f"Hata: {e}"
    elif command.startswith("BROWSE:"):
        url = command.replace("BROWSE:", "", 1)
        # Basit scraper (urllib)
        return f"Site içeriği kazınılıyor (Simüle): {url}"
    return f"Bilinmeyen Komut: {command}"

async def connect_and_listen():
    while True:
        try:
            print(f"📡 AZI Master Bağlantısı Deneniyor: {URI}")
            async with websockets.connect(URI) as websocket:
                print("✅ AZI Sınır Ucu (Edge) AKTİF. Yerel Zeka Hazır.")
                
                while True:
                    raw_data = await websocket.recv()
                    
                    # Master'dan gelen emir tipini belirle
                    if raw_data.startswith("PROCESS_REQUEST:"):
                        # AZI Master düşünme görevini Ajan'a devretti
                        data = json.loads(raw_data.replace("PROCESS_REQUEST:", "", 1))
                        prompt = data.get("prompt")
                        history = data.get("history", [])
                        
                        print(f"🧠 Yerel Zeka Düşünüyor: {prompt}")
                        answer = await call_local_llm(prompt, history)
                        await websocket.send(f"LLM_RESPONSE:{answer}")
                        
                    else:
                        # Standart Tool Komutu
                        print(f"⚡ Araç Komutu: {raw_data}")
                        result = execute_local_tool(raw_data)
                        await websocket.send(result)
                    
        except websockets.exceptions.ConnectionClosed as e:
            print(f"📡 Bağlantı Kapandı: {e}. 5 saniye sonra tekrar denenecek...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❌ Bağlantı Hatası: {e}")
            if "404" in str(e):
                print("⚠️ UYARI: URL bulunamadı. Lütfen Render'daki uygulama adınızı kontrol edin.")
            await asyncio.sleep(5)

if __name__ == "__main__":
    print("="*60)
    print("🤖 AZI EDGE AGENT (Yerel Zeka Motoru) BAŞLATILDI")
    print(f"Hedef Sunucu: {URI}")
    print("Mod: Yerel (Ollama) + Uzaktan Kontrol")
    print("="*60)
    try:
        asyncio.run(connect_and_listen())
    except KeyboardInterrupt:
        print("\nAjan kapatılıyor...")

