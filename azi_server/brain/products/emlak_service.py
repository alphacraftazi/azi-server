from sqlalchemy.orm import Session
from azi_server import models
import datetime
import json

class EmlakService:
    def sync_listings(self, db: Session, license_key: str, listings_data: list):
        """
        İstemciden gelen ilan listesini veritabanı ile senkronize eder.
        """
        stats = {"added": 0, "updated": 0, "total_processed": len(listings_data)}
        
        for item in listings_data:
            l_no = str(item.get("listing_no"))
            if not l_no: continue
            
            # Mevcut kaydı bul
            existing = db.query(models.RealEstateListing).filter(
                models.RealEstateListing.license_key == license_key,
                models.RealEstateListing.listing_no == l_no
            ).first()
            
            price_val = self._clean_price(item.get("price", 0))
            
            if existing:
                # Güncelleme Kontrolü
                is_changed = False
                if existing.price != price_val:
                    existing.price = price_val
                    existing.last_updated_at = datetime.datetime.utcnow()
                    is_changed = True
                    # Fiyat değişim logu eklenebilir
                    
                if is_changed:
                    stats["updated"] += 1
            else:
                # Yeni Kayıt
                new_listing = models.RealEstateListing(
                    license_key=license_key,
                    listing_no=l_no,
                    title=item.get("title", ""),
                    price=price_val,
                    location=item.get("location", ""),
                    m2=item.get("m2", ""),
                    rooms=item.get("rooms", ""),
                    floor=item.get("floor", ""),
                    phone=item.get("phone", ""),
                    url=item.get("url", ""),
                    category=item.get("category", "Genel"),
                    listing_type=item.get("listing_type", "Satılık"),
                    status="active"
                )
                db.add(new_listing)
                stats["added"] += 1
        
        db.commit()
        return stats

    def get_portfolio(self, db: Session, license_key: str):
        """Müşterinin portföyünü (sadece CRM'e eklenenleri veya hepsini) döndürür."""
        # Şimdilik hepsini döndürelim, filtreleme istemci tarafında yapılabilir
        listings = db.query(models.RealEstateListing).filter(
            models.RealEstateListing.license_key == license_key
        ).all()
        return listings

    def update_listing_status(self, db: Session, license_key: str, listing_no: str, updates: dict):
        """
        Not ekleme, duruma portföye alma vb.
        updates örn: {"status": "portfolio", "notes": "Arandı, randevu alındı"}
        """
        listing = db.query(models.RealEstateListing).filter(
            models.RealEstateListing.license_key == license_key,
            models.RealEstateListing.listing_no == listing_no
        ).first()
        
        if listing:
            if "status" in updates: listing.status = updates["status"]
            if "notes" in updates: listing.notes = updates["notes"]
            if "customer_interest" in updates: listing.customer_interest = updates["customer_interest"]
            if "appointment_date" in updates: 
                # Tarih formatı parse edilmeli
                try:
                    listing.appointment_date = datetime.datetime.fromisoformat(updates["appointment_date"])
                except: pass
                
            listing.last_updated_at = datetime.datetime.utcnow()
            db.commit()

            # --- AZI LEARNING INJECTION ---
            # Eğer satış gerçekleştiyse Azi bunu öğrenmeli
            if "status" in updates and updates["status"] == "Satıldı":
                try:
                    sale_price = updates.get("notes", "").split("Satış Fiyatı:")[-1].split(".")[0].strip()
                    memory_text = f"Emlak Satışı Gerçekleşti: İlan No {listing_no}, Bölge {listing.location}, Fiyat {sale_price} TL."
                    
                    # Log as fact
                    fact = models.AIMemory(
                        memory_type="fact",
                        content=memory_text,
                        timestamp=datetime.datetime.utcnow()
                    )
                    db.add(fact)
                    db.commit()
                    print(f"AZI LEARNED: {memory_text}")
                except Exception as e:
                    print(f"Learning Error: {e}")

            return {"status": "ok"}
        return {"error": "Listing not found"}

    def _clean_price(self, price_val):
        try:
            if isinstance(price_val, int): return price_val
            cleaned = "".join(filter(str.isdigit, str(price_val)))
            return int(cleaned) if cleaned else 0
        except: return 0

emlak_brain = EmlakService()
