
import sys
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Helper script to fix the leads table in the LOCAL database (azi_server/azi_system_v3.db)

DB_FILE = "azi_system_v3.db"
if not os.path.exists(DB_FILE):
    print(f"Warning: {DB_FILE} not found in current directory. Creating new one.")

engine = create_engine(f"sqlite:///{DB_FILE}")
Base = declarative_base()

# Redefine Lead based on models.py to ensure it matches
class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    phone = Column(String, nullable=True)
    source = Column(String) 
    sector = Column(String) 
    
    # Matching models.py definition
    trust_score = Column(Integer, default=50) 
    status = Column(String, default="new") 
    is_approved = Column(Integer, default=0) # THE MISSING COLUMN
    
    domain = Column(String, nullable=True) 
    notes = Column(Text, nullable=True) 
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_contacted = Column(DateTime, nullable=True)

print("Creating/Updating 'leads' table...")
try:
    Base.metadata.create_all(engine)
    print("Success: 'leads' table ensured.")
    
    # Verify
    from sqlalchemy import inspect
    inspector = inspect(engine)
    cols = [c['name'] for c in inspector.get_columns('leads')]
    if 'is_approved' in cols:
        print("Verified: 'is_approved' column exists.")
    else:
        print("ERROR: 'is_approved' column MISSING even after create_all!")
        
except Exception as e:
    print(f"Error: {e}")
