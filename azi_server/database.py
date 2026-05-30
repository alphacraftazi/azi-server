import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./azi_system_v3.db")

# Render postgres:// -> postgresql://
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

def _build_engine(url):
    connect_args = {"check_same_thread": False} if "sqlite" in url else {}
    return create_engine(url, connect_args=connect_args, pool_pre_ping=True)

# PostgreSQL'e bağlanmayı dene, başaramazsa SQLite'a düş
try:
    engine = _build_engine(SQLALCHEMY_DATABASE_URL)
    # Bağlantıyı hemen test et
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print(f"[DB] Bağlantı başarılı: {'PostgreSQL' if 'postgresql' in SQLALCHEMY_DATABASE_URL else 'SQLite'}")
except Exception as e:
    print(f"[DB] PostgreSQL bağlantısı başarısız: {e}")
    print("[DB] SQLite'a geçiliyor...")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./azi_system_v3.db"
    engine = _build_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
