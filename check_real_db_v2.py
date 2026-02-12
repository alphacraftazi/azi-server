
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Run from SCRATCH directory

# Add azi_server to path
sys.path.append(os.path.join(os.getcwd(), 'azi_server'))

try:
    from azi_server import models
    from azi_server import database
    from azi_server.brain import tools_smtp
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

# Correct Path to DB (since we are in scratch)
DB_PATH = os.path.join(os.getcwd(), 'azi_server', 'azi_system_v3.db')
print(f"Connecting to DB at: {DB_PATH}")

if not os.path.exists(DB_PATH):
    print("ERROR: DB file not found at expected path!")
    sys.exit(1)

engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    count = db.query(models.Lead).count()
    print(f"Total Leads: {count}")
    
    new_leads = db.query(models.Lead).filter(models.Lead.status == 'new').all()
    print(f"New Leads: {len(new_leads)}")

    if count == 0:
        print("No leads found. Inserting a test lead...")
        # Insert test lead
        test_lead = models.Lead(
            email="alpay.zorbek@alphacraftazi.com", 
            source="Manual Test",
            sector="test",
            status="new",
            trust_score=100
        )
        db.add(test_lead)
        db.commit()
        print("Inserted test lead: alpay.zorbek@alphacraftazi.com")
        new_leads = [test_lead] # Update list
        
    # Attempt to send to the first new lead (or the test one)
    if new_leads:
        target = new_leads[0]
        print(f"Attempting to send email to: {target.email}")
        try:
             res = tools_smtp.send_email_smtp(
                target.email,
                "AZI Customer Hunt Test",
                "Bu bir test mailidir. Müşteri avı sistemi onarıldı.\n\n(Bu mail 'new' durumundaki bir lead'e gönderildi)"
            )
             print(f"Send Result: {res}")
             
             # If success, update status? No, let user do it via app logic or just leave it for now.
        except Exception as e:
            print(f"Send Error: {e}")

except Exception as e:
    print(f"DB Operation Error: {e}")
