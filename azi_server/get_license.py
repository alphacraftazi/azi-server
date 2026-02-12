from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models_local import Business

# Connect to DB
SQLALCHEMY_DATABASE_URL = "sqlite:///../azi_system_v3.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Query for Staff product
print("Searching for Staff licenses...")
results = db.query(Business).filter(
    (Business.product_type.ilike('%personel%')) | 
    (Business.product_type.ilike('%staff%')) |
    (Business.name.ilike('%staff%'))
).all()

if results:
    for r in results:
        print(f"Product: {r.name}, Type: {r.product_type}, Key: {r.license_key}")
else:
    print("No Staff licenses found.")

# List all just in case
print("\n--- All Licenses ---")
all_res = db.query(Business).all()
for r in all_res:
    print(f"Product: {r.name}, Type: {r.product_type}, Key: {r.license_key}")
