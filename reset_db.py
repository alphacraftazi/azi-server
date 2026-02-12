import sqlite3
import os

DB_PATH = r"C:\Users\alpay\.gemini\antigravity\scratch\azi_system_v3.db"

def reset_db():
    if not os.path.exists(DB_PATH):
        print("Database file not found.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            if table_name != "sqlite_sequence": # Don't delete sequence
                print(f"Clearing table: {table_name}")
                cursor.execute(f"DELETE FROM {table_name}")
        
        conn.commit()
        conn.close()
        print("Database reset successfully via SQL.")
    except Exception as e:
        print(f"Error resetting DB: {e}")

if __name__ == "__main__":
    reset_db()
