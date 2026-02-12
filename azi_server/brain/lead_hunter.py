from duckduckgo_search import DDGS
import re
from sqlalchemy.orm import Session
from .. import models
import datetime

class LeadHunter:
    """
    İnternet üzerindeki potansiyel müşterileri bulur.
    Özellikle 'Zincir Cafe/Restoran' gibi odaklı aramalar yapar.
    """
    def __init__(self):
        self.email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        self.ddgs = DDGS()

    def search_leads(self, db: Session, sector: str = "cafe", limit: int = 20):
        """
        Belirtilen sektör için arama yapar ve bulunan mailleri kaydeder.
        Strateji: 'Account Based Marketing' (ABM) - Doğrudan büyük zincirleri hedefler.
        """
        
        # Hedef Zincir Listesi (Türkiye Odaklı - GENİŞLETİLMİŞ)
        target_chains = {
            "cafe": [
                "Starbucks Türkiye", "Kahve Dünyası", "Espressolab", "Arabica Coffee House", 
                "Mado", "Simit Sarayı", "Gönül Kahvesi", "Gloria Jean's Coffees Türkiye",
                "Tchibo Türkiye", "Caribou Coffee Türkiye", "Barnie's Coffee", "Soulmate Coffee",
                "Mackbear Coffee", "Coffy", "Viyana Kahvesi"
            ],
            "restaurant": [
                "Big Chefs", "Happy Moon's", "Cookshop", "Midpoint", "Huqqa", 
                "Nusr-Et", "Köfteci Yusuf", "Tavuk Dünyası", "Baydöner", 
                "HD İskender", "Burger King Türkiye Genel Müdürlük", "Mc Donalds Türkiye Genel Müdürlük",
                "Dominos Pizza Türkiye", "KFC Türkiye", "Popeyes Türkiye", "Dardenia"
            ],
            "real_estate": [
                "Remax Türkiye", "Coldwell Banker Türkiye", "Century 21 Türkiye", 
                "Turyap Genel Müdürlük", "Keller Williams Türkiye", "Era Gayrimenkul Türkiye",
                "Realty World Türkiye", "Startkey Gayrimenkul", "Premar Gayrimenkul"
            ],
            "retail": [
                "Migros Genel Müdürlük", "CarrefourSA Genel Müdürlük", "BİM Birleşik Mağazalar",
                "A101 Yeni Mağazacılık", "Şok Marketler", "Gratis", "Watsons Türkiye",
                "Teknosa", "Vatan Bilgisayar", "MediaMarkt Türkiye"
            ],
            "corporate": [
                "Koç Holding", "Sabancı Holding", "Eczacıbaşı Holding", "Doğuş Grubu",
                "Yıldız Holding", "Zorlu Holding", "Anadolu Grubu", "Kibar Holding"
            ]
        }
        
        # 'all' veya 'tumu' denirse hepsini tara
        if sector.lower() in ["all", "tumu", "tümü", "hepsi"]:
            sectors_to_scan = target_chains.keys()
        else:
            sectors_to_scan = [sector]
            
        found_leads = []
        
        for current_sector in sectors_to_scan:
            chains_to_hunt = target_chains.get(current_sector, [])
            if not chains_to_hunt: continue
            
            print(f"LEAD HUNTER: {current_sector.upper()} sektöründeki {len(chains_to_hunt)} büyük zincir için av başladı...")
            
            for chain in chains_to_hunt:
                # Global markalar için Türkiye ofisini zorla
                search_prefix = chain
                if "Türkiye" not in chain and "Turkey" not in chain and "Holding" not in chain:
                    search_prefix = f"{chain} Türkiye"
    
                # Her zincir için özel aramalar (Daha spesifik ve kapsamlı)
                queries = [
                    f'"{search_prefix}" "genel müdürlük" email',
                    f'"{search_prefix}" "insan kaynakları" iletisim',
                    f'site:linkedin.com "{search_prefix}" "purchasing" email',
                    f'"{chain}" franchising "başvuru" mail adresi',
                    f'"{chain}" kurumsal iletişim e-posta',
                    f'"{chain}" satınalma müdürü mail'
                ]
                
                print(f"   🔍 Hedef: {chain} (TR Odaklı)")
                
                for query in queries:
                    try:
                        # DuckDuckGo ile ara (Limit artırıldı)
                        # RateLimit durumunda bekleme eklendi
                        results = self.ddgs.text(query, max_results=5) 
                        
                        if not results:
                            continue
    
                        for r in results:
                            content = f"{r.get('title', '')} {r.get('body', '')} {r.get('snippet', '')}"
                            emails = re.findall(self.email_regex, content)
                            
                            for email in emails:
                                email = email.lower().strip()
                                
                                # Spam Filtresi
                                if any(x in email for x in ["wix", "sentry", "noreply", "domain", "example", ".png", ".jpg", ".gif", "u00", "imge", "image"]):
                                    continue
                                
                                if len(email) < 5 or "." not in email.split("@")[-1]:
                                    continue
                                    
                                # Türkiye / Kurumsal Kontrol
                                notes = f"Hedef: {chain}"
                                trust_bonus = 0
                                if ".tr" in email: trust_bonus += 30
                                if "info" in email: trust_bonus += 10
                                if "ik" in email or "hr" in email or "kariyer" in email: trust_bonus += 20
                                
                                # Veritabanında var mı?
                                exists = db.query(models.Lead).filter(models.Lead.email == email).first()
                                if not exists:
                                    new_lead = models.Lead(
                                        email=email,
                                        source=f"Targeted: {chain}", 
                                        sector=current_sector,
                                        domain=email.split('@')[-1],
                                        trust_score=50 + trust_bonus, 
                                        status="new",
                                        notes=notes
                                    )
                                    db.add(new_lead)
                                    found_leads.append(f"{chain}: {email}")
                                    print(f"      💰 BULUNDU: {email} (Skor: {50 + trust_bonus})")
                                else:
                                    pass 
                    
                    except Exception as e:
                        # Eğer RateLimit hatası ise bekle
                        if "Ratelimit" in str(e):
                            print("      ⏳ KOTA DOLDU (Rate Limit). 15 saniye soğutma molası...")
                            import time
                            time.sleep(15)
                        else:
                            print(f"      ⚠️ Hata ({chain}): {e}")
    
        db.commit()
        return found_leads



hunter_service = LeadHunter()
