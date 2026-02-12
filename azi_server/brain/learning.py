import os
import datetime

class SelfLearner:
    """
    Azi'nin kendi kod tabanını ve yeteneklerini öğrenmesini sağlayan modül.
    (Meta-Cognition / Self-Awareness)
    """
    
    def __init__(self, root_dir=None):
        if not root_dir:
            # varsayılan olarak 2 üst klasör (scratch root)
            self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        else:
            self.root_dir = root_dir
            
        self.knowledge_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "azi_knowledge.md")

    def scan_codebase(self):
        """
        Proje klasörlerini tarar ve önemli dosyaların özetlerini çıkarır.
        """
        summary = f"# AZI ÖZ-BİLİNÇ VE SİSTEM HAFIZASI\n\nTarih: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        summary += "Aşağıda, senin (Azi) ve parçası olduğun sistemlerin teknik yapısı bulunmaktadır. Bunu kendini anlamak için kullan.\n\n"
        
        target_dirs = ["azi_server", "azi_app", "alpha_craft_stok", "AlphaCraftPro2", "alpha_emlak_pro"]
        
        for d in target_dirs:
            full_path = os.path.join(self.root_dir, d)
            if os.path.exists(full_path):
                summary += f"## Modül: {d}\n"
                
                # Önemli dosyaları bul
                for root, dirs, files in os.walk(full_path):
                    if "__pycache__" in root or "node_modules" in root or ".git" in root or "dist" in root:
                        continue
                        
                    for file in files:
                        if file.endswith(".py") or file.endswith(".js") or file.endswith(".html"):
                            # Sadece ana dosyalar veya önemli scriptler
                            if file in ["main.py", "logic.py", "blackbox.js", "city_crm.js", "index.html", "dashboard.html", "main_pro2.py"]:
                                file_path = os.path.join(root, file)
                                try:
                                    with open(file_path, "r", encoding="utf-8") as f:
                                        content = f.read()
                                        
                                        # Dosya açıklaması veya docstring bulmaya çalış
                                        desc = "Açıklama yok."
                                        if file.endswith(".py") and '"""' in content[:200]:
                                            desc = content.split('"""')[1].strip()
                                        elif file.endswith(".js") and "//" in content[:100]:
                                            desc = content.split("\n")[0].replace("//", "").strip()
                                            
                                        summary += f"- **{file}**: {desc[:150].replace(chr(10), ' ')}...\n"
                                except: pass
                summary += "\n"
                
        # Stok ve Pro2 Analizi
        summary += "\n## ÜRÜN ANALİZLERİ (Öğrenilenler)\n"
        
        # Stok
        stok_path = os.path.join(self.root_dir, "alpha_craft_stok", "main.py")
        if os.path.exists(stok_path):
            summary += "- **Alpha Stok**: PyWebview tabanlı. Lisans kontrolü var. Stok giriş/çıkış ve kritik seviye takibi yapıyor.\n"
            
        # Pro2
        pro_path = os.path.join(self.root_dir, "AlphaCraftPro2", "main_pro2.py")
        if os.path.exists(pro_path):
             summary += "- **Alpha Staff v2 (Pro2)**: Personel takip sistemi. QR kod, vardiya ve bordro özellikleri var. 'alpha_craft_data_v3_clean' klasörüne veri kaydeder.\n"
        
        return summary

    def learn(self):
        """Öğrenme işlemini başlatır ve dosyaya kaydeder."""
        knowledge = self.scan_codebase()
        with open(self.knowledge_file, "w", encoding="utf-8") as f:
            f.write(knowledge)
        return "Öz-bilinç güncellendi."

# Tekil kullanım
learner = SelfLearner()
