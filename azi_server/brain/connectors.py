import os
import sqlite3
import json
from pathlib import Path

class DataConnector:
    """
    Alpha Craft Ekozistemindeki diğer uygulamaların veritabanlarına bağlanır.
    (Read-Only Access for Dashboard)
    """
    
    def __init__(self):
        # Proje kök dizini (azi_server/brain/connectors.py -> .../scratch/)
        self.root_dir = Path(__file__).parent.parent.parent
        
        # Veritabanı Yolları (Tahmini ve Standartlar)
        self.db_paths = {
            "stok": self.root_dir / "alpha_craft_stok" / "stok.db", # Veya orders.db
            "staff": self.root_dir / "AlphaCraftPro2" / "alpha_craft_data_v3_clean" / "personel.db",
            "emlak": self.root_dir / "alpha_emlak_pro" / "emlak.db"
        }
        
    def _get_connection(self, app_name):
        path = self.db_paths.get(app_name)
        if path and path.exists():
            try:
                conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True) # Read-Only Mode
                conn.row_factory = sqlite3.Row
                return conn
            except Exception as e:
                print(f"CONNECTOR ERROR ({app_name}): {e}")
                return None
        return None

    def get_stock_stats(self):
        """Stok programından özet veriler"""
        # Stok DB yapısını bilmiyorsak güvenli fail
        path = self.root_dir / "alpha_craft_stok" / "data" / "alpha_stok.db" # Tahmin
        
        # Alternatif: Stok programı JSON kullanıyorsa?
        # Genelde Alpha Stok JSON kullanıyordu. Kontrol edelim.
        json_path = self.root_dir / "alpha_craft_stok" / "data" / "inventory.json"
        
        stats = {"revenue": 0, "low_stock": 0, "total_items": 0}
        
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    stats["total_items"] = len(data)
                    stats["low_stock"] = sum(1 for x in data if int(x.get("quantity", 0)) < 5)
                    # Revenue hesabı zor (satış geçmişi lazım), şimdilik item değeri
                    stats["stock_value"] = sum(float(x.get("price", 0)) * int(x.get("quantity", 0)) for x in data)
            except: pass
            
        return stats

    def get_staff_stats(self):
        """Personel programından veriler"""
        # Pro2 genelde JSON kullanıyor olabilir mi?
        # Dosyalara bakmak lazım ama şimdilik placeholder dönelim
        return {"active_staff": 0, "on_leave": 0}

    def get_global_revenue(self):
        """Tüm sistemin tahmini cirosunu hesaplar"""
        stock = self.get_stock_stats()
        # Emlak ve Staff eklenecek
        
        # Şimdilik AZI Lisans gelirlerini server DB'den çekmek daha garantili
        return stock.get("stock_value", 0) # Placeholder

connector_service = DataConnector()
