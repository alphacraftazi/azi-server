from azi_server import database, models
from sqlalchemy.orm import Session

def check_memory():
    db = database.SessionLocal()
    try:
        # Fact, system_log veya user_message içinde mail/smtp ara
        keywords = ["mail", "smtp", "şifre", "password", "@", "host", "port"]
        
        print("--- TARAMA BAŞLATILIYOR ---")
        
        # 1. Facts (Öğrenilen Bilgiler)
        facts = db.query(models.AIMemory).filter(models.AIMemory.memory_type == "fact").all()
        for f in facts:
            if any(k in f.content.lower() for k in keywords):
                print(f"[FACT] {f.content}")

        # 2. User Messages (Son 100 mesajda ara)
        msgs = db.query(models.AIMemory).filter(models.AIMemory.memory_type == "user_message").order_by(models.AIMemory.id.desc()).limit(200).all()
        for m in msgs:
            if any(k in m.content.lower() for k in keywords):
                print(f"[USER] ({m.timestamp}) {m.content}")

    finally:
        db.close()

if __name__ == "__main__":
    check_memory()
