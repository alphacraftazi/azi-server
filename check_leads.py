
import sys
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Add azi_server to path
sys.path.append(os.path.join(os.getcwd(), 'azi_server'))

try:
    from azi_server import models
    from azi_server import database
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

# Connect to DB
try:
    models.Base.metadata.create_all(bind=database.engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database.engine)
    db = SessionLocal()
except Exception as e:
    print(f"DB Error: {e}")
    sys.exit(1)

# Query Leads
leads_count = db.query(models.Lead).count()
print(f"Total Leads: {leads_count}")

new_leads = db.query(models.Lead).filter(models.Lead.status == 'new').all()
print(f"New Leads (Ready to Send): {len(new_leads)}")

contacted_leads = db.query(models.Lead).filter(models.Lead.status == 'contacted').all()
print(f"Contacted Leads: {len(contacted_leads)}")

if len(new_leads) > 0:
    print("\nSample New Leads:")
    for lead in new_leads[:5]:
        print(f" - {lead.email} (Score: {lead.trust_score})")

if len(contacted_leads) > 0:
    print("\nSample Contacted Leads:")
    for lead in contacted_leads[:5]:
        print(f" - {lead.email} (Last Contact: {lead.last_contacted})")
