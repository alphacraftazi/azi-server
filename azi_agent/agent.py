import sys
import os
import json
import asyncio
import websockets

# Proje kök dizinini Python yoluna ekle ki tools_pc.py kütüphanesini içeri aktarabilelim
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from azi_server.brain import tools_pc

# Ana Beyin (Render Sunucusu) Adresi
URI = "wss://azi-server.onrender.com/ws/agent"

# Eğer LOKALDE test etmek isterseniz üsttekinin başına # koyup alttakini açın:
# URI = "ws://localhost:8000/ws/agent"

async def connect_and_listen():
    while True:
        try:
            print(f"📡 Ana Beyin'e (AZI Master) bağlanılıyor: {URI}")
            async with websockets.connect(URI) as websocket:
                print("✅ Bağlantı başarılı! Sinir ucu aktif, emirler bekleniyor...")
                
                while True:
                    command = await websocket.recv()
                    print(f"⚡ Emir Alındı: {command}")
                    
                    response = ""
                    if command == "PC_STATUS":
                        response = tools_pc.get_system_status()
                    elif command.startswith("TERM:"):
                        cmd = command.replace("TERM:", "", 1)
                        response = tools_pc.run_system_command(cmd)
                    elif command.startswith("KILL:"):
                        pname = command.replace("KILL:", "", 1)
                        response = tools_pc.kill_process(pname)
                    else:
                        response = f"Bilinmeyen ajan emri: {command}"
                        
                    print(f"📤 Sonuç Ana Beyin'e Raporlanıyor...")
                    await websocket.send(response)
                    
        except websockets.exceptions.ConnectionClosed:
            print("⚠️ Bağlantı Ana Beyin tarafından kesildi. 5 saniye içinde tekrar deneniyor...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❌ Ağ veya Bağlantı Hatası: {e}")
            print("Yeniden bağlanılıyor...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    print("="*60)
    print("🤖 AZI OMNIPRESENT AGENT (Sinir Ucu Ajanı) BAŞLATILDI")
    print("Bu pencere açık kaldığı sürece AZI (Render) bilgisayarınıza hükmedebilir.")
    print("="*60)
    asyncio.run(connect_and_listen())
