
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Lead, Base # Assuming running inside azi_server where models.py is

DB_FILE = "azi_system_v3.db"
engine = create_engine(f"sqlite:///{DB_FILE}")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print(f"Checking DB: {DB_FILE}")

try:
    count = db.query(Lead).count()
    print(f"Total Leads: {count}")
    
    new_leads = db.query(Lead).filter(Lead.status == 'new').all()
    print(f"New Leads: {len(new_leads)}")
    
    if count == 0:
        print("No leads found. Inserting a test lead...")
        # Insert a test lead with USER's likely email (or placeholder) to test sending
        test_lead = Lead(
            email="alpay.zorbek@alphacraftazi.com", 
            source="Manual Test",
            sector="test",
            status="new",
            trust_score=100
        )
        db.add(test_lead)
        db.commit()
        print("Inserted test lead: alpay.zorbek@alphacraftazi.com")
        
    # Test sending (simulate SEND_PRESENTATION logic)
    # We can import tools_smtp if we add parent to path? No, tools_smtp is in brain.
    # sys.path.append(os.path.join(os.getcwd(), 'brain')) # brain is module inside azi_server
    
    try:
        from brain import tools_smtp
        print("Imported tools_smtp successfully.")
        
        # Try to send to the first new lead
        if new_leads:
            print(f"Attempting to send to first new lead: {new_leads[0].email}")
            res = tools_smtp.send_email_smtp(
                new_leads[0].email,
                "AZI Customer Hunt Test",
                "Bu bir test mailidir. Müşteri avı sistemi onarıldı."
            )
            print(f"Send Result: {res}")
        elif count > 0: # If we just inserted one
             test_l = db.query(Lead).filter(Lead.email == "alpay.zorbek@alphacraftazi.com").first()
             if test_l:
                 print(f"Attempting to send to test lead: {test_l.email}")
                 res = tools_smtp.send_email_smtp(
                    test_l.email,
                    "AZI Customer Hunt Test",
                    "Bu bir test mailidir. Müşteri avı sistemi onarıldı."
                )
                 print(f"Send Result: {res}")
                 
    except ImportError as e:
         print(f"Could not import tools_smtp: {e}")
         # Attempt to fix path
         sys.path.append(os.getcwd()) # azi_server
         try:
             from brain import tools_smtp
             print("Imported tools_smtp (retry).")
         except:
             print("Failed to import tools_smtp.")

except Exception as e:
    print(f"DB Error: {e}")
