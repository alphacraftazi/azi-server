from sqlalchemy.orm import Session
from .. import models
import datetime
import secrets
import uuid
import json

class ProductManager:
    """
    Alpha Craft ürünleri için lisanslama ve yönetim sistemi.
    """
    
    def create_business(self, db: Session, name: str, product_type: str, details_json: str = "{}", price: float = 0.0):
        # Lisans anahtarı üret (UUID4)
        key = str(uuid.uuid4()).upper()
        
        new_biz = models.Business(
            name=name,
            license_key=key,
            product_type=product_type,
            details=details_json,
            license_price=price,
            status="active",
            last_seen=datetime.datetime.utcnow()
        )
        db.add(new_biz)
        db.commit()
        db.refresh(new_biz)
        return new_biz

    def delete_business_by_id(self, db: Session, biz_id: int):
        try:
            biz = db.query(models.Business).filter(models.Business.id == biz_id).first()
            if not biz:
                return {"success": False, "error": "İşletme bulunamadı"}
            
            # İlişkili logları sil
            db.query(models.DataLog).filter(models.DataLog.business_id == biz_id).delete()
            db.delete(biz)
            db.commit()
            return {"success": True}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}

    def update_status(self, db: Session, license_key: str, status: str = "online"):
        """
        Sadece durum ve son görülme zamanını günceller (Komut tüketmez).
        """
        business = db.query(models.Business).filter(models.Business.license_key == license_key).first()
        if business:
            business.last_seen = datetime.datetime.utcnow()
            business.is_online = 1 if status == "online" else 0
            db.commit()
            return True
        return False

    def verify_license(self, db: Session, license_key: str, system_info: dict = None):
        """
        Lisans anahtarını doğrular ve sistem bilgisini günceller.
        """
        business = db.query(models.Business).filter(models.Business.license_key == license_key).first()
        if business and business.status == "active":
            # Son görülme zamanını güncelle
            business.last_seen = datetime.datetime.utcnow()
            business.is_online = 1
            
            # Sistem bilgisi geldiyse güncelle
            if system_info:
                business.system_info = json.dumps(system_info, ensure_ascii=False)
            
            # --- KOMUT KUYRUĞU KONTROLÜ ---
            pending_cmd = db.query(models.CommandQueue).filter(
                models.CommandQueue.license_key == license_key,
                models.CommandQueue.status == "pending"
            ).order_by(models.CommandQueue.created_at.asc()).first()
            
            response = {"valid": True, "business_name": business.name, "id": business.id}
            
            if pending_cmd:
                response["command"] = pending_cmd.command
                try:
                    # Args JSON string ise parse etmeden gonder (Client parse etsin veya API JSON gondersin)
                    # Ama veritabanında TEXT tutuyoruz, o yuzden string gelecek.
                    response["args"] = json.loads(pending_cmd.args)
                except:
                    response["args"] = {}
                
                # Durumu güncelle
                pending_cmd.status = "delivered"
                
            db.commit()
            return response
        return {"valid": False}

    def queue_command(self, db: Session, license_key: str, command: str, args: dict = {}):
        """Kuyruğa yeni komut ekler."""
        new_cmd = models.CommandQueue(
            license_key=license_key,
            command=command,
            args=json.dumps(args, ensure_ascii=False),
            status="pending",
            created_at=datetime.datetime.utcnow()
        )
        db.add(new_cmd)
        db.commit()
        return new_cmd

    def get_dashboard_cards(self, db: Session):
        """
        Dashboard kartları için özet veriler hazırlar.
        """
        try:
            businesses = db.query(models.Business).all()
            cards = []
            
            today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            for biz in businesses:
                try:
                    # 1. Temel Bilgiler
                    card = {
                        "id": biz.id,
                        "name": biz.name,
                        "type": biz.product_type,
                        "license_key": biz.license_key,
                        # "is_online": biz.is_online == 1,
                        # Better Logic: Trust timestamp
                        "is_online": (datetime.datetime.utcnow() - biz.last_seen).total_seconds() < 120 if biz.last_seen else False,
                        # UTC string sonuna 'Z' ekle ki JS bunu UTC olarak algılasın ve yerel saate çevirsin
                        "last_seen": f"{biz.last_seen.isoformat()}Z" if biz.last_seen else None,
                        "status": "normal",
                        "alert_message": "",
                        "today_revenue": 0.0,
                        "personnel": 0,
                        "products": 0
                    }

                    # 2. Detayları Parse Et
                    try:
                        details = json.loads(biz.details or "{}")
                        card["personnel"] = details.get("personnel", 0)
                        card["products"] = details.get("products", 0)
                    except: pass

                    # 3. Ciro Hesapla
                    # data_type='daily_sales' logları
                    # HATA OLABİLİR: DataLog tablosu boşsa veya timestamp sorunu varsa
                    # Basitlik için sadece sorguyu yapıyoruz, hata verirse 0 kabul et.
                    try:
                        daily_logs = db.query(models.DataLog).filter(
                            models.DataLog.business_id == biz.id,
                            models.DataLog.data_type == 'daily_sales',
                            models.DataLog.timestamp >= today_start
                        ).all()

                        revenue = 0.0
                        for log in daily_logs:
                             if not log.content: continue
                             try:
                                data = json.loads(log.content)
                                if isinstance(data, list):
                                     for day in data:
                                         if isinstance(day, dict) and 'total' in day:
                                             revenue += float(day['total'])
                             except: pass
                        card["today_revenue"] = revenue
                    except Exception as e_log:
                        print(f"Log Error for {biz.name}: {e_log}")

                    # 4. Durum Analizi
                    if biz.last_seen:
                        time_diff = datetime.datetime.utcnow() - biz.last_seen
                        if time_diff.total_seconds() > 3600:
                            card["status"] = "warning"
                            card["alert_message"] = "UZUN SÜREDİR OFFLINE"
                    
                    cards.append(card)
                except Exception as e_inner:
                    print(f"Error processing business {biz.name}: {e_inner}")
                    continue

            return cards
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"CRITICAL ERROR in get_dashboard_cards: {e}")
            return []

    def sync_data(self, db: Session, license_key: str, data_type: str, content: dict):
        """
        İstemciden gelen veriyi veritabanına kaydeder.
        """
        business = db.query(models.Business).filter(models.Business.license_key == license_key).first()
        if not business:
            return {"success": False, "error": "Invalid license"}

        # Veriyi logla
        log = models.DataLog(
            business_id=business.id,
            data_type=data_type,
            content=json.dumps(content, ensure_ascii=False),
            timestamp=datetime.datetime.utcnow()
        )
        db.add(log)
        
        # Son görülme zamanını güncelle ve ONLINE yap
        business.last_seen = datetime.datetime.utcnow()
        business.is_online = 1 # EKLENDİ: Sinyal geldiyse onlinedır.
        
        db.commit()
        return {"success": True}

    def get_all_businesses(self, db: Session):
        """Tüm kayıtlı işletmeleri listeler."""
        return db.query(models.Business).all()

    def delete_all_businesses(self, db: Session):
        """Tüm işletme kayıtlarını siler."""
        try:
            # Önce child tabloları (DataLog) silmek gerekebilir ama cascade varsa otomatik olur.
            # Garanti olsun diye önce logları silelim.
            db.query(models.DataLog).delete() 
            db.query(models.Business).delete()
            db.commit()
            return {"success": True}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}

product_service = ProductManager()
