import sqlite3
import os
import json

DB_PATH = r"C:\Users\alpay\.gemini\antigravity\scratch\azi_system_v3.db"

def check_db():
    report = {"status": "unknown", "tables": {}, "integrity": "unknown"}
    
    if not os.path.exists(DB_PATH):
        report["status"] = "missing_file"
        print(json.dumps(report, indent=4))
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check Integrity
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        report["integrity"] = integrity_result
        
        # Get Tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            t_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {t_name}")
            count = cursor.fetchone()[0]
            report["tables"][t_name] = count
            
        report["status"] = "online"
        conn.close()
        
    except Exception as e:
        report["status"] = "error"
        report["error"] = str(e)
        
    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    check_db()
