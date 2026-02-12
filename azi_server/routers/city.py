from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import UserActivity
import datetime
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/city",
    tags=["city"]
)

# Pydantic Models
class ActivityCreate(BaseModel):
    activity_type: str
    title: str
    description: str = ""
    latitude: float
    longitude: float

class ActivityOut(BaseModel):
    id: int
    activity_type: str
    title: str
    description: str
    latitude: float
    longitude: float
    date: datetime.datetime
    ai_insight: str = ""

    class Config:
        orm_mode = True

@router.get("/activities", response_model=list[ActivityOut])
def get_activities(db: Session = Depends(get_db)):
    """
    Tüm aktif aktiviteleri getirir.
    """
    return db.query(UserActivity).filter(UserActivity.status == "active").order_by(UserActivity.date.desc()).all()

@router.post("/activities", response_model=ActivityOut)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    """
    Harita üzerinde yeni bir aktivite (pin, not) oluşturur.
    """
    db_item = UserActivity(
        activity_type=activity.activity_type,
        title=activity.title,
        description=activity.description,
        latitude=activity.latitude,
        longitude=activity.longitude,
        date=datetime.datetime.utcnow()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/activities/{activity_id}")
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    """
    Aktiviteyi siler (arşivler).
    """
    item = db.query(UserActivity).filter(UserActivity.id == activity_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    item.status = "archived"
    db.commit()
    return {"success": True}

@router.get("/analysis")
def get_analysis(db: Session = Depends(get_db)):
    """
    Azi'nin şehir aktiviteleri üzerindeki analizi.
    (Şimdilik dummy datalarla)
    """
    count = db.query(UserActivity).filter(UserActivity.status == "active").count()
    
    analysis_text = "Henüz yeterli veri yok."
    if count > 5:
        analysis_text = f"Haritada {count} nokta işaretlendi. Yoğunluk 'Tepebaşı' bölgesinde artıyor. Tavsiye: Batıkent tarafına ziyaret planlayın."
    elif count > 0:
        analysis_text = "İlk veriler işleniyor. Ping atılan bölgeler ticari potansiyel taşıyor."
        
    return {"analysis": analysis_text, "count": count}
