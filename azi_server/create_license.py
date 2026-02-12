from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models_local import Business
import uuid
import datetime

# Connect to DB (Parent Dir)
SQLALCHEMY_DATABASE_URL = "sqlite:///../azi_system_v3.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Check if already exists (incase of race condition or previous run)
existing = db.query(Business).filter(Business.product_type == 'personel').first()
if existing:
    print(f"EXISTING_KEY:{existing.license_key}")
else:
    # Create new
    key = str(uuid.uuid4()).upper()
    new_biz = Business(
        name="Alpha Staff Kurumsal",
        license_key=key,
        product_type="personel", # Must match what main_pro2.py expects or logic
        status="active",
        details='{"personnel": 10, "products": 0}',
        last_seen=datetime.datetime.utcnow(),
        is_online=0
    )
    db.add(new_biz)
    db.commit()
    print(f"NEW_KEY:{key}")
