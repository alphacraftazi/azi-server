import sqlite3
import os

DB_FILE = "azi_system_v3.db"

def upgrade_database():
    if not os.path.exists(DB_FILE):
        print(f"HATA: Veritabanı dosyası bulunamadı: {DB_FILE}")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Leads tablosunun sütunlarını kontrol et
        cursor.execute("PRAGMA table_info(leads)")
        columns = [info[1] for info in cursor.fetchall()]

        if "is_approved" not in columns:
            print("Sütun ekleniyor: is_approved...")
            cursor.execute("ALTER TABLE leads ADD COLUMN is_approved INTEGER DEFAULT 0")
            conn.commit()
            print("BAŞARILI: Veritabanı güncellendi! Verileriniz korundu.")
        else:
            print("BİLGİ: Sütun zaten mevcut. İşlem gerekmiyor.")

    except Exception as e:
        print(f"HATA OLUŞTU: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_database()
