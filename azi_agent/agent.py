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
                    elif command.startswith("FS_LIST:"):
                        path = command.replace("FS_LIST:", "", 1)
                        try:
                            # Eger nokta ise calistigi dizini ver
                            target_path = os.getcwd() if path == "." else path
                            items = os.listdir(target_path)
                            # Liste uzayabilecegi icin 100 item ile sinirla
                            items = items[:100]
                            response = f"Klasör içeriği ({target_path}):\n" + "\n".join(items)
                        except Exception as e:
                            response = f"FS_LIST Hatası: {e}"
                    elif command.startswith("FS_READ:"):
                        path = command.replace("FS_READ:", "", 1)
                        try:
                            with open(path, "r", encoding="utf-8") as f:
                                # Ilk 5000 karakterini dondur (veri cok buyuk olmamasi adina)
                                content = f.read(5000)
                                response = f"Dosya ({path}):\n\n```\n{content}\n```"
                        except Exception as e:
                            response = f"FS_READ Hatası: {e}"
                    elif command.startswith("FS_WRITE:"):
                        parts = command.replace("FS_WRITE:", "", 1).split("|", 1)
                        if len(parts) == 2:
                            path = parts[0]
                            import base64
                            content = base64.b64decode(parts[1]).decode("utf-8")
                            try:
                                # Ust klasorleri otomatik olustur (write_to_file davranişi)
                                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                                with open(path, "w", encoding="utf-8") as f:
                                    f.write(content)
                                response = f"Dosya başarıyla kaydedildi/yazıldı: {path}"
                            except Exception as e:
                                response = f"FS_WRITE Hatası: {e}"
                        else:
                            response = "Hatalı FS_WRITE formatı."
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
