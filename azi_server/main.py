from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict # Added for connection manager
from azi_server import models, database
from azi_server.brain import proactive, logic, analysis, voice, core_products, vision as brain_vision, weather # Added weather
from azi_server.routers import city
import asyncio
import json
import os
import datetime
from azi_server.brain.notifications import notifier # Added Notification Service

# --- WEBSOCKET MANAGER REMOVED (Duplicate) ---
# Unified ConnectionManager is defined below.


# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="AZI: Alpha Craft Intelligence")

@app.on_event("startup")
async def startup_event():
    print("\n\n" + "="*50)
    print("AZI SERVER STARTING... SITE REQUESTS MODULE ACTIVE")
    print("="*50 + "\n\n")
    
    # Notify Admin Mobile
    await notifier.send_async(
        title="AZI: İletişim Hattı Açık",
        message="Sistem başarıyla başlatıldı. Sinyal gücü %100.",
        priority=2,
        tags=["satellite", "computer"]
    )
app.include_router(city.router)
from azi_server.routers import telemetry
app.include_router(telemetry.router)
from azi_server.routers import factory
app.include_router(factory.router)
# Vision Router issue bypass: Defining directly
# app.include_router(vision.router)

import sys
# Ngrok Support
try:
    from pyngrok import ngrok, conf
    # Optional: Set auth token if user provides it later
    # conf.get_default().auth_token = "YOUR_TOKEN"
except ImportError:
    print("Ngrok module not found. Install with: pip install pyngrok")

# Global Public URL
import builtins
builtins.AZI_PUBLIC_URL = None

@app.on_event("startup")
async def start_ngrok_tunnel():
    """Start Ngrok Tunnel on Startup"""
    try:
        # Check if already running to avoid duplicates in reload
        tunnels = ngrok.get_tunnels()
        if not tunnels:
            # Open a HTTP tunnel on the default port 8001
            # If you have a static domain (paid), use: domain="kendi-domainin.ngrok.io"
            public_url = ngrok.connect(8001).public_url
            print(f"\n\n{'='*60}")
            print(f" AZI GLOBAL ACCESS ENABLED ")
            print(f" Public URL: {public_url}")
            print(f"{'='*60}\n\n")
            builtins.AZI_PUBLIC_URL = public_url
        else:
            builtins.AZI_PUBLIC_URL = tunnels[0].public_url
            print(f"AZI Existing Public URL: {builtins.AZI_PUBLIC_URL}")
            
    except Exception as e:
        print(f"Ngrok Startup Error: {e}")
        # Fallback to LAN IP
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            builtins.AZI_PUBLIC_URL = f"http://{s.getsockname()[0]}:8001"
            s.close()
        except:
            builtins.AZI_PUBLIC_URL = "http://127.0.0.1:8001"
            
    # Update Status
    if builtins.AZI_PUBLIC_URL:
        # Notify Admin if notifier is ready
        pass

class EvaluateReq(BaseModel):
    image: str
    prompt: str = "Bunu analiz et"

@app.get("/vision_test")
async def vision_test():
    """Görüş sistemi testi (Sunucunun güncel olup olmadığını anlamak için)."""
    return {"status": "Vision System Online", "timestamp": str(datetime.datetime.utcnow())}

@app.get("/api/monitor/website")
async def monitor_website():
    """Web sitesinin durumunu kontrol eder."""
    import requests
    import time
    try:
        start = time.time()
        # Ping the site (timeout 2s is plenty for basic check)
        r = requests.get("https://alphacraftazi.com", timeout=3)
        elapsed = int((time.time() - start) * 1000)
        
        if r.status_code == 200:
            return {"status": "ONLINE", "ping": elapsed, "code": 200}
        else:
            return {"status": "ERROR", "ping": elapsed, "code": r.status_code}
    except Exception as e:
         return {"status": "OFFLINE", "ping": 0, "error": str(e)}

@app.post("/vision_scan")
async def analyze_image_direct(req: EvaluateReq):
    """Kameradan gelen görüntüyü yapay zekaya yorumlatır (Root Direct Endpoint)."""
    # Debug log
    # print(f"VISION REQUEST RECEIVED: {len(req.image)} bytes") 
    
    result = brain_vision.vision_service.analyze_frame(req.image, req.prompt)
    
    # Hata varsa bile 200 OK dönelim ki frontend mesajı gösterebilsin (Quota Error vb.)
    # 500 dönünce frontend çöküyor.
    return result


# CORS (Tarayıcı erişimi için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Öncelikli: WebSocket (Bunu en üste yakın tutuyoruz ki ezilmesin)
# main.py dosyasının en altındaki websocket_endpoint zaten tanımlı.

# Frontier (Arayüz) Dosyalarını Sun - EN SONA EKLENMELİ
# Arayuz ayarlari asagiya tasindi (WebSocket cakismasini onlemek icin)

# Canlı bağlantılar (WebSockets)
# Canlı bağlantılar (WebSockets)
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.client_map: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if client_id:
            self.client_map[client_id] = websocket
            print(f"Client {client_id} connected via Legacy/Mobile endpoint")

    def disconnect(self, websocket: WebSocket = None, client_id: str = None):
        # Duruma göre temizlik yap
        if websocket and websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if client_id and client_id in self.client_map:
            ws = self.client_map[client_id]
            if ws in self.active_connections:
                self.active_connections.remove(ws)
            del self.client_map[client_id]
            print(f"Client {client_id} disconnected.")

    async def broadcast(self, message: str, msg_type: str = "response", action: str = None):
        """Tüm bağlı cihazlara mesaj (ve varsa aksiyon) gönderir."""
        payload = {
            "type": msg_type,
            "message": message,
            "action": action,
            "timestamp": str(datetime.datetime.utcnow())
        }
        await self.broadcast_json(payload)

    async def broadcast_json(self, payload: dict):
        """Hazır JSON payload gönderir."""
        # Kopuk bağlantıları temizlemek için kopya üzerinde dön
        for connection in self.active_connections[:]: 
            try:
                await connection.send_json(payload)
            except Exception as e:
                print(f"Yayın Hatası (Removing): {e}")
                if connection in self.active_connections:
                    self.active_connections.remove(connection)

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.client_map:
            try:
                await self.client_map[client_id].send_json(message)
            except:
                self.disconnect(client_id=client_id)

manager = ConnectionManager()

# GLOBAL ACCESS FOR LOGIC (Unified)
import builtins
builtins.ws_manager = manager

@app.on_event("startup")
async def startup_event():
    """Sunucu başladığında AZI uyanır."""
    print("AZI: Sistem başlatılıyor... Hafıza yükleniyor...")
    # Proaktif beyni arka planda başlat
    asyncio.create_task(proactive.start_monitoring(manager))

# read_root kaldirildi, static files halledecek

def get_db():
    """Veritabanı oturumu sağlar."""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        # --- GEÇMİŞ YÜKLEME (SENKRONİZASYON) ---
        # Son 50 mesajı çek (Sadece kullanıcı ve AZI konuşmaları)
        history = db.query(models.AIMemory).filter(
            models.AIMemory.memory_type.in_(["user_message", "azi_response"])
        ).order_by(models.AIMemory.id.desc()).limit(50).all()
        
        # Kronolojik sıraya sok (Eskiden yeniye)
        history.reverse()
        
        # Geçmişi tek tek gönder
        for record in history:
            role = "azi" if record.memory_type == "azi_response" else "user"
            await websocket.send_json({
                "type": "history_sync",
                "sender": role,
                "message": record.content,
                "timestamp": str(record.timestamp)
            })

        # Karşılama
        await websocket.send_json({"type": "greeting", "message": "Bağlantı senkronize edildi. Alpay Bey, sistemler aktif."})
            
        while True:
            data = await websocket.receive_text()
            
            # Logic Katmanına Gönder
            result = logic.brain_service.process(data, db)
            
            # --- ACTION HANDLER (COMMAND QUEUE) ---
            act = result.get("action")
            if act and act.startswith("client_command:"):
                try:
                    # Format: client_command:LICENSE:CMD:ARGS_JSON
                    parts = act.split(":", 3)
                    if len(parts) >= 4:
                        l_key = parts[1]
                        cmd_name = parts[2]
                        args_val = json.loads(parts[3])
                        
                        # Kuyruğa Ekle
                        products.product_service.queue_command(db, l_key, cmd_name, args_val)
                except Exception as e:
                    print(f"Command Queue Error: {e}")
            
            # Cevabı Gönder
            response_payload = {
                "type": "response",
                "message": result["text"],
                "action": result["action"],
                "timestamp": str(datetime.datetime.utcnow())
            }
            
            # --- SES ÜRETİMİ (GELİŞMİŞ) ---
            # İstemcinin "ses açık" olup olmadığını bilmiyoruz ama URL gönderirsek
            # istemci çalmak isterse çalar.
            # Uzun metinlerde gecikme olabilir, bu yüzden asenkron yapılması daha iyi olurdu ama
            # şimdilik basit tutuyoruz.
            # Sadece kısa cevaplar veya düz metinler için üretelim (Kod blokları hariç)
            if result["text"] and len(result["text"]) < 500 and "```" not in result["text"]:
                audio_url = await voice.voice_service.generate_audio(result["text"])
                if audio_url:
                    response_payload["audio_url"] = audio_url

            await manager.broadcast_json(response_payload)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket Hatası: {e}")
        manager.disconnect(websocket)

async def process_command(data: str):
    """
    Gelen komutu AZI'nin beynine gönderir.
    """
    db = database.SessionLocal()
    try:
        # logic.process artik bir dict donuyor: {"text":Str, "action":Str|None}
        result = logic.brain_service.process(data, db)
        
        response_payload = {
            "type": "response",
            "message": result["text"]
        }
        
        # Eger ozel bir aksiyon varsa onu da ekle
        if result["action"]:
            response_payload["action"] = result["action"]
            
    finally:
        db.close()

# --- ÜRÜN & LİSANS YÖNETİMİ (API) ---
from pydantic import BaseModel

class LicenseCheck(BaseModel):
    license_key: str
    system_info: dict | None = None

class DataSync(BaseModel):
    license_key: str
    data_type: str
    content: dict

class NewBusiness(BaseModel):
    name: str
    product_type: str
    details: dict | None = None # Wizard'dan gelen veriler
    price: float = 0.0 # Lisans Bedeli

@app.post("/api/license/check")
async def check_license(req: LicenseCheck, db: Session = Depends(get_db)):
    """İstemci uygulamanın lisansını kontrol eder."""
    return core_products.product_service.verify_license(db, req.license_key, req.system_info)

@app.post("/api/license/create")
async def create_license(req: NewBusiness, db: Session = Depends(get_db)):
    """Yeni bir işletme ve lisans anahtarı oluşturur."""
    details_json = json.dumps(req.details, ensure_ascii=False) if req.details else "{}"
    res = core_products.product_service.create_business(db, req.name, req.product_type, details_json, req.price)
    return {"status": "created", "license_key": res.license_key, "id": res.id}

@app.post("/api/sync")
async def sync_client_data(req: DataSync, db: Session = Depends(get_db)):
    """İstemciden gelen verileri (ciro, stok vb.) kaydeder."""
    return core_products.product_service.sync_data(db, req.license_key, req.data_type, req.content)

@app.get("/api/businesses")
async def list_businesses(db: Session = Depends(get_db)):
    """Tüm işletmeleri listeler."""
    return core_products.product_service.get_all_businesses(db)

@app.get("/api/telemetry/cards")
async def get_dashboard_cards(db: Session = Depends(get_db)):
    """Dashboard için kart verilerini döndürür."""
    return core_products.product_service.get_dashboard_cards(db)

@app.delete("/api/license/{biz_id}")
async def delete_single_license(biz_id: int, db: Session = Depends(get_db)):
    """Belirli bir işletmeyi siler."""
    return core_products.product_service.delete_business_by_id(db, biz_id)

@app.post("/api/license/delete-all")
async def delete_all_licenses(db: Session = Depends(get_db)):
    """Tüm lisansları ve verileri tamamen siler (Force delete)."""
    print("DEBUG: Delete request received via POST")
    return core_products.product_service.delete_all_businesses(db)

@app.delete("/api/license/delete-all")
async def delete_all_licenses_alt(db: Session = Depends(get_db)):
    """(Alternatif) DELETE metodunu destekler."""
    print("DEBUG: Delete request received via DELETE")
    return products.product_service.delete_all_businesses(db)

@app.get("/api/system/version")
async def get_system_version():
    return {"version": "1.5.0", "timestamp": str(datetime.datetime.utcnow())}

# --- EMLAK CRM API ---
from .brain.products import emlak_service, automated_scraper

class EmlakSyncReq(BaseModel):
    license_key: str
    listings: list

class EmlakUpdateReq(BaseModel):
    license_key: str
    listing_no: str
    updates: dict

@app.post("/api/emlak/sync")
async def sync_emlak_data(req: EmlakSyncReq, db: Session = Depends(get_db)):
    """İstemci (Scraper) tarafından toplanan verileri sunucuya yedekler."""
    return emlak_service.emlak_brain.sync_listings(db, req.license_key, req.listings)

@app.get("/api/emlak/portfolio")
async def get_emlak_portfolio(license_key: str, db: Session = Depends(get_db)):
    """Sunucudaki yedeklenmiş portföyü çeker."""
    return emlak_service.emlak_brain.get_portfolio(db, license_key)

@app.post("/api/emlak/update")
async def update_emlak_listing(req: EmlakUpdateReq, db: Session = Depends(get_db)):
    """Tek bir ilanın durumunu/notunu günceller."""
    return emlak_service.emlak_brain.update_listing_status(db, req.license_key, req.listing_no, req.updates)

@app.post("/api/emlak/sale")
async def report_sale(req: EmlakUpdateReq, db: Session = Depends(get_db)):
    """
    Satılan/Arşivlenen ilanı Azi'ye bildirir.
    Bu önemli: Kullanıcının satış başarısını Azi bilmeli.
    """
    # Güncelleme mantığı aynıdır, sadece semantik fark var
    return emlak_service.emlak_brain.update_listing_status(db, req.license_key, req.listing_no, req.updates)

@app.post("/api/emlak/run_scraper")
async def run_scraper_bot(db: Session = Depends(get_db)):
    """
    Botu manuel olarak tetikler.
    Gerçek senaryoda bu işlem uzun sürdüğü için BackgroundTasks ile yapılmalı ama
    şimdilik blocking olarak çalışacak (basitlik için).
    """
    return automated_scraper.bot_instance.run()

# --- FABRİKA (BUILD) API ---
from .brain import factory
from fastapi.responses import FileResponse

@app.post("/api/factory/package/{license_key}")
async def package_client(license_key: str, db: Session = Depends(get_db)):
    """Belirtilen lisans anahtarı için özel kurulum paketi hazırlar."""
    # Lisans anahtarına ait işletmeyi bul ve ürün tipini al
    biz = db.query(models.Business).filter(models.Business.license_key == license_key).first()
    product_type = biz.product_type if biz else "stock" # Varsayılan stock
    
    custom_req = None
    if biz and biz.details:
        try:
            dets = json.loads(biz.details)
            custom_req = dets.get("custom_requirements")
        except:
            pass

    res = factory.factory_service.package_client(license_key, product_type, custom_requirements=custom_req, business_name=biz.name if biz else "Business")
    return res

@app.get("/api/factory/download/{filename}")
async def download_installer(filename: str):
    """Hazırlanan paketi indirir."""
    # Güvenlik: Sadece izin verilen klasörden indirme yap
    installers_path = factory.factory_service.installers_path
    file_path = os.path.join(installers_path, filename)
    
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/zip', filename=filename)
    else:
        return {"error": "Dosya bulunamadı"}

# --- ANALİZ API ---
@app.get("/api/analysis/trends")
async def get_trends(db: Session = Depends(get_db)):
    return analysis.analysis_service.get_weekly_revenue_trend(db)

@app.get("/api/analysis/health")
async def get_health(db: Session = Depends(get_db)):
    return analysis.analysis_service.get_system_health(db)

# --- KONTROL API ---
class CommandReq(BaseModel):
    license_key: str
    command: str
    args: dict = {}

@app.post("/api/control/send")
async def send_command_manual(req: CommandReq, db: Session = Depends(get_db)):
    """Manuel olarak komut gönderir."""
    products.product_service.queue_command(db, req.license_key, req.command, req.args)
    return {"status": "queued", "target": req.license_key}

# --- MOBILE ENTEGRASYON API ---
class VoiceReq(BaseModel):
    text: str
    client_id: str

class TelemetryReq(BaseModel):
    lat: float = 0.0
    lon: float = 0.0
    acc: float = 0
    spd: float = 0
    bat: int = 0
    ping: bool = False

# Basit in-memory storage (DB'ye gerek yok simdilik)
user_telemetry_data = {"lat": 0, "lon": 0, "last_seen": None}

@app.post("/api/chat/voice")
async def chat_voice(req: VoiceReq, db: Session = Depends(get_db)):
    """Mobilden gelen sesli (metne dönüşmüş) komutları işler."""
    
    # 0. Broadcast User Message to all screens (Desktop Dashboard sees what you said)
    await manager.broadcast_json({
        "type": "history_sync", 
        "sender": "user",
        "message": req.text,
        "timestamp": str(datetime.datetime.utcnow())
    })

    # 1. Logic İşleme
    result = logic.brain_service.process(req.text, db)
    
    # 2. Voice Generation (Edge-TTS) - Natural Voice
    audio_url = None
    # Only generate if text is reasonable length and not code
    if result["text"] and len(result["text"]) < 500 and "```" not in result["text"]:
        try:
            audio_url = await voice.voice_service.generate_audio(result["text"])
        except Exception as e:
            print(f"Voice Gen Error: {e}")

    # 3. Broadcast AZI Message to all screens (So Desktop hears it too)
    await manager.broadcast_json({
        "type": "response",
        "message": result["text"],
        "action": result["action"],
        "audio_url": audio_url, # Desktop plays this
        "timestamp": str(datetime.datetime.utcnow())
    })
    
    # 4. Return to Mobile Caller
    return {
        "text": req.text,
        "response": result["text"],
        "action": result["action"],
        "audio_url": audio_url # Mobile plays this
    }

@app.post("/api/telemetry/user_location")
async def receive_location(req: TelemetryReq):
    """Telefondan gelen GPS verisini kaydeder."""
    # Ping ise sadece last_seen guncelle
    user_telemetry_data["last_seen"] = str(datetime.datetime.utcnow())
    
    if not req.ping:
        user_telemetry_data["lat"] = req.lat
        user_telemetry_data["lon"] = req.lon
        user_telemetry_data["acc"] = req.acc
        user_telemetry_data["spd"] = req.spd
        
    return {"status": "ok"}

@app.get("/api/telemetry/user_location")
async def get_user_location():
    """Dashboard haritası için son konumu döndürür."""
    return user_telemetry_data

# --- SITE REQUESTS (MOVED UP BEFORE STATIC MOUNT) ---
class SiteReqCreate(BaseModel):
    name: str
    company: str
    contact_info: str
    product_interest: str
    note: str

@app.post("/api/requests/create")
async def create_site_request(req: SiteReqCreate, db: Session = Depends(get_db)):
    """Web sitesinden gelen form talebini kaydeder."""
    new_req = models.SiteRequest(
        name=req.name,
        company=req.company,
        contact_info=req.contact_info,
        product_interest=req.product_interest,
        note=req.note
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    
    # --- NEURAL LINK NOTIFICATION ---
    try:
        # Broadcast to Mobile & Dashboard
        asyncio.create_task(manager.broadcast_json({
            "type": "notification",
            "title": "YENİ SİTE TALEBİ",
            "message": f"{req.company} firmasından yeni talep var.",
            "data": {"id": new_req.id, "name": req.name},
            "sound": "alert"
        }))
        
        # Proactive Voice Trigger (Speak to mobile)
        asyncio.create_task(manager.broadcast_json({
            "type": "speak",
            "text": f"Dikkat. {req.company} firmasından yeni bir iş talebi ulaştı.",
            "trigger_voice": True
        }))
        
        # --- NTFY BACKGROUND PUSH ---
        asyncio.create_task(notifier.send_async(
            title="YENİ SİTE TALEBİ!",
            message=f"{req.company} firmasından talep var.\nÜrün: {req.product_interest}\nNot: {req.note[:50]}...",
            priority=4, # High Priority
            tags=["bell", "moneybag"]
        ))
        
    except Exception as e:
        print(f"Notification Error: {e}")

    return {"status": "success", "id": new_req.id}

@app.get("/api/requests/active")
async def get_active_site_requests(db: Session = Depends(get_db)):
    """Henüz incelenmemiş (new) talepleri getirir."""
    reqs = db.query(models.SiteRequest).filter(models.SiteRequest.status == "new").order_by(models.SiteRequest.created_at.desc()).all()
    return reqs

@app.post("/api/requests/{req_id}/archive")
async def archive_site_request(req_id: int, db: Session = Depends(get_db)):
    """Talebi arşivler (status=reviewed)."""
    r = db.query(models.SiteRequest).filter(models.SiteRequest.id == req_id).first()
    if r:
        r.status = "reviewed"
        db.commit()
        return {"status": "archived"}
    raise HTTPException(404, "Request not found")

@app.delete("/api/requests/{req_id}")
async def delete_site_request(req_id: int, db: Session = Depends(get_db)):
    """Talebi siler."""
    r = db.query(models.SiteRequest).filter(models.SiteRequest.id == req_id).first()
    if r:
        db.delete(r)
        db.commit()
        return {"status": "deleted"}
    raise HTTPException(404, "Request not found")

# Frontier (Arayüz) Dosyalarını Sun - EN SONA EKLENMELİ
# WebSocket gibi ozel rotalar yukarida tanimlandi, simdi geri kalan her seyi arayuze yonlendiriyoruz.
current_dir = os.path.dirname(os.path.realpath(__file__))
app_dir = os.path.join(os.path.dirname(current_dir), "azi_app")
audio_dir = os.path.join(app_dir, "audio_cache")

# --- API ENDPOINTS MUST BE BEFORE STATIC MOUNT ---

class ChatReq(BaseModel):
    text: str

@app.get("/api/brain/stream")
def get_brain_stream():
    """Frontend polls this to see if AZI wants to speak."""
    if azi_brain.voice_queue:
        thought = azi_brain.voice_queue.pop(0)
        return {"speak": thought, "mood": azi_brain.mood}
    return {"speak": None}





# --- WEBSITE MONITORING (NEW) ---
import urllib.request
import time

@app.get("/api/monitor/website")
async def monitor_website_status():
    """Checks if alphacraftazi.com is online."""
    url = "https://alphacraftazi.com"
    try:
        start = time.time()
        # Blocking call but short timeout
        code = urllib.request.urlopen(url, timeout=3).getcode()
        duration = int((time.time() - start) * 1000)
        
        if code == 200:
            return {"status": "online", "latency": duration}
    except Exception as e:
        print(f"Monitor Error: {e}")
        pass
        
    return {"status": "offline", "latency": 0}

# --- WEBSOCKET ENDPOINT (MUST BE BEFORE STATIC MOUNT) ---
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        # Bağlanınca hemen hava durumunu söyle (İlk Jest)
        try:
            briefing = weather.get_daily_briefing()
            await manager.send_personal_message({"type": "speak", "text": briefing}, client_id)
        except Exception as w_warn:
            print(f"Weather error (ignoring): {w_warn}")

        while True:
            # Client'tan gelen mesajları dinle
            data = await websocket.receive_json()
            if "lat" in data:
                # GPS vb.
                pass

    except WebSocketDisconnect:
        manager.disconnect(client_id=client_id)
    except Exception as e:
        print(f"WS Handler Error: {e}")
        manager.disconnect(client_id=client_id)

# Audio Cache klasörü yoksa oluştur (voice.py zaten yapıyor ama garanti olsun)
if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

app.mount("/audio_cache", StaticFiles(directory=audio_dir), name="audio")
# Website Static Files (For Local Testing)
website_dir = os.path.join(os.path.dirname(current_dir), "alphacraft_website")
app.mount("/static/website", StaticFiles(directory=website_dir, html=True), name="website")

# app.mount("/", StaticFiles(directory=app_dir, html=True), name="ui") 
# MOVED TO BOTTOM

# --- AUTOMATED BACKGROUND TASKS ---
@app.on_event("startup")
async def schedule_background_tasks():
    loop = asyncio.get_event_loop()
    loop.create_task(weekly_emlak_scheduler())

async def weekly_emlak_scheduler():
    """Haftalık Emlak Botu Zamanlayıcısı"""
    print("[SCHEDULER] Emlak Botu Zamanlayıcısı Başlatıldı.")
    while True:
        try:
            now = datetime.datetime.now()
            # Pazar günü (6) ve sabah 09:00 - 10:00 arası (tekrarı önlemek için basit kontrol)
            # Gerçek bir cron job daha iyidir ama bu basit çözüm MVP için yeterli.
            # Test için: now.minute % 10 == 0 gibi sık çalıştırılabilir. 
            # Kullanıcı isteği: "Her Pazar günü"
            
            # STATE DOSYASI İLE KONTROL (Günde 1 kereden fazla çalışmasın)
            last_run_file = "emlak_last_run.txt"
            last_run_date = ""
            if os.path.exists(last_run_file):
                with open(last_run_file, "r") as f: last_run_date = f.read().strip()
            
            today_str = now.strftime("%Y-%m-%d")
            
            # Pazar günü ve bugün henüz çalışmadıysa
            if now.weekday() == 6 and last_run_date != today_str:
                print("[SCHEDULER] Pazar Günü Güncellemesi Başlıyor...")
                
                # Run Scraper (Blocking olduğu için thread'de çalıştıralım veya await edelim)
                # automated_scraper.bot_instance.run() senkron bir metot.
                # Blocking olmaması için run_in_executor kullanabiliriz.
                
                # NOTE: run_scraper_bot içindeki fonksiyon blocking.
                automated_scraper.bot_instance.run()
                
                # Kaydet
                with open(last_run_file, "w") as f: f.write(today_str)
                print("[SCHEDULER] Güncelleme Tamamlandı.")

            # Her 1 saatte bir kontrol et
            await asyncio.sleep(3600) 
            
        except Exception as e:
            print(f"[SCHEDULER ERROR] {e}")
            await asyncio.sleep(3600)

# --- ROUTER REGISTER ---
@app.get("/api/analysis/executive")
async def get_executive_summary():
    """Tüm ekosistem verilerini (Stok, Emlak, Personel) döner"""
    return logic.brain_service.get_executive_summary()

# --- LEAD HUNTER API ---
class LeadUpdateReq(BaseModel):
    lead_id: int
    status: str # 'new', 'contacted', 'replied'
    notes: Optional[str] = None

@app.get("/api/leads")
async def get_leads(db: Session = Depends(get_db)):
    """Tüm potansiyel müşterileri getirir."""
    leads = db.query(models.Lead).order_by(models.Lead.created_at.desc()).all()
    
    # İstatistikler
    stats = {
        "total": len(leads),
        "new": len([l for l in leads if l.status == "new"]),
        "contacted": len([l for l in leads if l.status == "contacted"]),
        "replied": len([l for l in leads if l.status == "replied"]),
        "pending_approval": len([l for l in leads if l.is_approved == 0]),
    }
    
    return {"leads": leads, "stats": stats}

class LeadApprovalReq(BaseModel):
    lead_id: int
    approved: bool # True: Onayla, False: Reddet (Sil veya Arşivle)

@app.post("/api/leads/approve")
async def approve_lead(req: LeadApprovalReq, db: Session = Depends(get_db)):
    """Müşteriyi onaylar veya reddeder."""
    lead = db.query(models.Lead).filter(models.Lead.id == req.lead_id).first()
    if lead:
        lead.is_approved = 1 if req.approved else -1
        db.commit()
        return {"status": "updated", "approved": req.approved}
    raise HTTPException(status_code=404, detail="Lead not found")    

@app.post("/api/leads/update")
async def update_lead_status(req: LeadUpdateReq, db: Session = Depends(get_db)):
    """Bir müşterinin durumunu günceller (Örn: Cevap verdi için)"""
    lead = db.query(models.Lead).filter(models.Lead.id == req.lead_id).first()
    if lead:
        lead.status = req.status
        if req.notes:
            lead.notes = req.notes
        db.commit()
        return {"status": "updated", "lead_id": lead.id, "new_status": lead.status}
    raise HTTPException(status_code=404, detail="Lead not found")
    
    raise HTTPException(status_code=404, detail="Lead not found")
    


from fastapi import BackgroundTasks

@app.post("/api/leads/scan")
async def trigger_deep_scan(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Derinlemesine taramayı arka planda başlatır.
    """
    # Background Task olarak ekle (Main thread'i kilitlemesin)
    background_tasks.add_task(run_deep_scan_task)
    return {"status": "started", "message": "Derin tarama arka planda başlatıldı."}

def run_deep_scan_task():
    """
    Arka planda çalışacak tarama görevi.
    Yeni bir DB session açmalı çünkü dependency session kapanmış olabilir.
    """
    try:
        print("[DEEP SCAN] Arka plan görevi başladı...")
        new_db = database.SessionLocal()
        hunter = lead_hunter.LeadHunter()
        hunter.search_leads(new_db, "all", limit=50)
        new_db.close()
        print("[DEEP SCAN] Görev tamamlandı.")
    except Exception as e:
        print(f"[DEEP SCAN ERROR] {e}")


# (Websocket endpoint moved up)

# (Websocket vs. yukarıda)

app.mount('/', StaticFiles(directory=app_dir, html=True), name='ui')
