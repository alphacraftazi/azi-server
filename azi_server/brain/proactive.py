import asyncio
import random
import json

async def start_monitoring(manager):
    """
    Proaktif İzleme ve Otomasyon Sistemi
    
    1. Haftalık Veri Güncelleme (Pazar 03:00)
    2. Sistem Sağlığı Kontrolü (Placeholder)
    """
    print("AZI Brain: Otomasyon sistemleri devrede. Haftalık güncelleme takvimi: Pazar 03:00")
    
    from .products import automated_scraper
    import datetime
    
    # Botun tekrar tekrar çalışmasını önlemek için flag
    last_run_date = None

    while True:
        try:
            now = datetime.datetime.now()
            
            # HAFTALIK GÜNCELLEME (Pazar = 6, Saat = 3)
            # Eğer gün Pazar ise ve saat 03 ise VE bugün daha önce çalışmadıysa
            if now.weekday() == 6 and now.hour == 3:
                today_str = now.strftime("%Y-%m-%d")
                
                if last_run_date != today_str:
                    print(f"AZI: Haftalık güncelleme başlatılıyor... ({today_str})")
                    await manager.broadcast_json({"type": "info", "message": "Sistem Bakımı: Haftalık veri güncellemesi başlatıldı."})
                    
                    # Bloklamamak için Thread havuzunda çalıştır
                    loop = asyncio.get_event_loop()
                    scraper = automated_scraper.ScraperBot()
                    # Botun run metodu senkron olduğu için run_in_executor kullanıyoruz
                    result = await loop.run_in_executor(None, scraper.run)
                    
                    if result.get("success"):
                        print("AZI: Güncelleme başarıyla tamamlandı.")
                        await manager.broadcast_json({"type": "success", "message": "Bakım Tamamlandı: Piyasa verileri güncellendi."})
                    else:
                        print(f"AZI: Güncelleme hatası: {result.get('msg')}")
                        await manager.broadcast_json({"type": "error", "message": f"Bakım Hatası: {result.get('msg')}"})
                    
                    last_run_date = today_str
            
        except Exception as e:
            print(f"AZI Monitoring Hatası: {e}")

        await asyncio.sleep(3600) # 1 saatte bir kontrol et
