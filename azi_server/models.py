from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class Business(Base):
    """
    Alpha Craft ürünlerini kullanan işletmeler.
    """
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    license_key = Column(String, unique=True, index=True)
    product_type = Column(String) # 'stok', 'personel', 'dershane' vb.
    status = Column(String, default="active")
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Yeni Eklenenler (Business Card)
    system_info = Column(Text, default="{}") # JSON: {pc_name, os, ram, ip}
    is_online = Column(Integer, default=0) # 0: Offline, 1: Online
    
    # Yeni Eklenenler (Yönetim & Wizard)
    # Yeni Eklenenler (Yönetim & Wizard)
    details = Column(Text, default="{}") # JSON: {personnel_count, product_count, sector, etc.}
    license_price = Column(Float, default=0.0) # Tahsil edilen ücret

    logs = relationship("DataLog", back_populates="business")

class DataLog(Base):
    """
    İşletmelerden gelen ham veriler (satış, devamsızlık vb.)
    AZI bu verileri analiz eder.
    """
    __tablename__ = "data_logs"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    data_type = Column(String) # 'satis', 'yoklama', 'giris'
    content = Column(Text) # JSON formatında detaylı veri
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    business = relationship("Business", back_populates="logs")

class AIMemory(Base):
    """
    AZI'nin öğrendiği şeyler ve sizinle olan konuşmaları.
    """
    __tablename__ = "ai_memories"

    id = Column(Integer, primary_key=True, index=True)
    memory_type = Column(String) # 'conversation', 'fact', 'rule'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class CommandQueue(Base):
    """
    İstemcilere gönderilecek komut kuyruğu.
    """
    __tablename__ = "command_queue"

    id = Column(Integer, primary_key=True, index=True)
    license_key = Column(String, index=True) # Hangi lisansa gidecek?
    command = Column(String) # 'shutdown', 'popup', 'lock'
    args = Column(Text, default="{}") # JSON parametreler
    status = Column(String, default="pending") # pending, delivered, executed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class RealEstateListing(Base):
    """
    Emlak CRM verileri. Hem Azi hafızasında hem de Client senkronizasyonunda kullanılır.
    """
    __tablename__ = "real_estate_listings"

    id = Column(Integer, primary_key=True, index=True)
    license_key = Column(String, index=True) # Hangi müşteriye ait?
    listing_no = Column(String, index=True) # Sahibinden No
    
    # Temel Veriler
    title = Column(String)
    price = Column(Integer)
    location = Column(String)
    m2 = Column(String)
    rooms = Column(String)
    floor = Column(String)
    phone = Column(String)
    url = Column(String)
    
    # Kategori
    category = Column(String) # Konut / İş Yeri
    listing_type = Column(String) # Satılık / Kiralık
    
    # CRM Durumları
    status = Column(String, default="active") # active, portfolio, sold, deleted
    notes = Column(Text, default="") # Müşteri notları
    customer_interest = Column(String, default="none") # hot, warm, cold
    appointment_date = Column(DateTime, nullable=True) # Randevu tarihi
    
    first_seen_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class UserActivity(Base):
    """
    Şehir CRM aktiviteleri. (Ping, Mark, Note, Visit)
    """
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    activity_type = Column(String) # 'ping', 'mark', 'note', 'visit'
    title = Column(String)
    description = Column(Text, default="")
    latitude = Column(Float)
    longitude = Column(Float)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="active") # active, archived
    
    # AI Analizi için
    ai_insight = Column(Text, default="") # Azi'nin bu aktivite hakkındaki yorumu

class Lead(Base):
    """
    Müşteri Avcısı (Lead Generation) Modülü için Potansiyel Müşteriler
    """
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    phone = Column(String, nullable=True)
    source = Column(String) # Google, DuckDuckGo, Manuel, vs.
    sector = Column(String) # 'cafe', 'restaurant', 'real_estate'
    
    # Skorlama ve Durum
    trust_score = Column(Integer, default=50) # 0-100 Güvenilirlik
    status = Column(String, default="new") # new, contacted, converted, bounced
    is_approved = Column(Integer, default=0) # 0: Pending, 1: Approved, -1: Rejected
    
    # Metadata
    domain = Column(String, nullable=True) # gmail.com, sirket.com
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_contacted = Column(DateTime, nullable=True)

class SiteRequest(Base):
    """
    Web sitesinden gelen 'Mühendis Talep Et' form verileri.
    """
    __tablename__ = "site_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    company = Column(String)
    contact_info = Column(String) # Tel veya Mail
    product_interest = Column(String)
    note = Column(Text)
    
    status = Column(String, default="new") # new, reviewed, contacted
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
