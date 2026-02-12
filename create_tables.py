
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add azi_server to path
sys.path.append(os.path.join(os.getcwd(), 'azi_server'))

try:
    from azi_server import models
    from azi_server import database
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

print("Creating all tables defined in models.py...")
try:
    models.Base.metadata.create_all(bind=database.engine)
    print("Tables created successfully.")
except Exception as e:
    print(f"Error creating tables: {e}")
    sys.exit(1)

# Verify leads table exists
try:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database.engine)
    db = SessionLocal()
    # Query leads (should be empty but not error)
    count = db.query(models.Lead).count()
    print(f"Verified: 'leads' table exists. Current count: {count}")
    
    # Check for is_approved column (indirectly via model access)
    # create_all should create it with the column if model has it
    lead = models.Lead(email="test@test.com", is_approved=1)
    db.add(lead)
    db.commit()
    print("Verified: Can insert into leads table with is_approved column.")
    
    # Cleanup (id auto increment, find the one we just added)
    db.delete(lead)
    db.commit()
    print("Cleanup: Deleted test lead.")
    
except Exception as e:
    print(f"Verification Error: {e}")
