from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models
import datetime
import json

from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models
import datetime
import json

class AnalysisManager:
    """
    İşletme verilerini analiz ederek içgörü ve özetler oluşturur.
    Gelişmiş Versiyon: Çoklu Ürün Desteği
    """
    
    def get_weekly_revenue_trend(self, db: Session):
        """Son 7 günün toplam cirosunu hesaplar (Sadece Stok ve Satış yapan ürünler için)."""
        try:
            today = datetime.datetime.utcnow().date()
            start_date = today - datetime.timedelta(days=6)
            
            # 1. Telemetry Üzerinden Gelen Satış Verilerini Çek
            # (Şuan 'daily_sales' olarak loglanan veriler)
            logs = db.query(models.DataLog).filter(
                models.DataLog.data_type == 'daily_sales',
                models.DataLog.timestamp >= start_date
            ).all()
            
            daily_totals = { (start_date + datetime.timedelta(days=i)): 0.0 for i in range(7) }
            
            for log in logs:
                try:
                    log_date = log.timestamp.date()
                    if log_date not in daily_totals: continue
                        
                    data = json.loads(log.content)
                    # Esnek Veri Okuma
                    val = 0
                    if isinstance(data, dict):
                        val = float(data.get('total', 0) or data.get('revenue', 0) or 0)
                    elif isinstance(data, list) and data:
                        val = float(data[0].get('total', 0) or 0)
                        
                    daily_totals[log_date] += val
                except:
                    continue
                    
            # 2. Return Chart Data
            trend = []
            for d, total in daily_totals.items():
                trend.append({"date": d.strftime("%Y-%m-%d"), "revenue": total})
            return trend
            
        except Exception as e:
            print(f"Analysis Error: {e}")
            return []

    def get_system_health(self, db: Session):
        """Sisteme bağlı işletmelerin sağlık durumunu puanlar."""
        businesses = db.query(models.Business).all()
        total_biz = len(businesses)
        if total_biz == 0:
            return {"score": 100, "status": "Boş", "active": 0, "total": 0, "details": []}
            
        active_count = 0
        details = []
        product_breakdown = {}
        
        for biz in businesses:
            # 1 Saat kuralı
            is_active = False
            if biz.last_seen:
                diff = datetime.datetime.utcnow() - biz.last_seen
                if diff.total_seconds() < 3600:
                    is_active = True
                    active_count += 1
            
            # Ürün Dağılımı
            p_type = biz.product_type or "unknown"
            product_breakdown[p_type] = product_breakdown.get(p_type, 0) + 1
            
            details.append({
                "name": biz.name,
                "type": p_type,
                "status": "Online" if is_active else "Offline",
                "last_seen": str(biz.last_seen)
            })
            
        score = int((active_count / total_biz) * 100) if total_biz > 0 else 0
        return {
            "score": score, 
            "active": active_count, 
            "total": total_biz, 
            "products": product_breakdown,
            "details": details
        }

    def generate_brief_for_azi(self, db: Session):
        """AZI için doğal dilde Gelişmiş Sistem Özeti."""
        health = self.get_system_health(db)
        trend = self.get_weekly_revenue_trend(db)
        
        total_rev_7d = sum(item['revenue'] for item in trend)
        
        # Breakdown Summary
        products_str = ", ".join([f"{k.upper()}: {v}" for k, v in health.get('products', {}).items()])
        
        summary = (
            f"--- EKO-SİSTEM DURUM RAPORU ---\n"
            f"📡 AĞ DURUMU: %{health['score']} Aktif\n"
            f"🏢 TOPLAM DÜĞÜM: {health['total']} İşletme ({health['active']} Online)\n"
            f"📦 DAĞILIM: [{products_str}]\n"
            f"💰 HAFTALIK AKIŞ: {total_rev_7d:,.0f} TL\n"
        )
        
        if health['score'] < 30:
            summary += "⚠️ KRİTİK: Ağın büyük çoğunluğu koptu. Bağlantı sorunları olabilir.\n"
        elif health['score'] == 100:
            summary += "✅ MÜKEMMEL: Tüm sistemler çevrimiçi ve stabil.\n"
            
        return summary

analysis_service = AnalysisManager()
