import os

# Sunum Dosyalarının Yolları
# Not: Yolları dinamik bulmak daha iyi olabilir ama şimdilik hardcoded.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # scratch
PRESENTATION_DIR = os.path.join(BASE_DIR, "Alpha_Sunumlar_TekDosya")

PRODUCTS = {
    "stock": {
        "name": "Alpha Stok & Envanter",
        "file": "Alpha_Stock_Sunum_Mobil.html",
        "subject": "⚠️ İşletmenizde Görünmeyen Giderleri Durdurun",
        "body": """
        Merhaba,
        
        İşletmelerin %40'ı, sadece "yönetilmeyen stok" yüzünden her yıl cirolarının %10'unu kaybediyor. Sizin deponuzda neler oluyor?
        
        <b>Alpha Stok</b> ile kontrolü saniyeler içinde geri alın:
        
        🔴 <b>Kayıp/Kaçak Önleme:</b> Ürünleriniz nereye gidiyor? Anında tespit edin.
        ⚡ <b>QR Kod Hızı:</b> Sayım yapmak artık işkence değil, saniyelik bir işlem.
        📊 <b>Kârlılık Analizi:</b> Hangi ürün rafta tozlanıyor, hangisi para basıyor?
        
        Size sadece bir yazılım değil, <b>uyumayan bir depo müdürü</b> öneriyoruz.
        
        Sistemin tüm yeteneklerini ve size özel teklifimizi ekteki interaktif sunumda bulabilirsiniz.
        
        <br>
        <div style="background-color: #f8f9fa; border-left: 4px solid #e74c3c; padding: 10px; margin-top: 15px; font-style: italic;">
        <b>💡 BİLİYOR MUYDUNUZ?</b><br>
        Alpha Craft Intelligence olarak sadece paket program satmıyoruz.<br>
        İşletmenizin en karmaşık, en "çözülmez" sanılan sorunu ne ise, <b>ona özel yapay zeka sistemi geliştiriyoruz.</b><br>
        Bize derdinizi anlatın, size çözümünü kodlayalım.
        </div>
        
        Saygılarımla,
        """
    },
    "crm": {
        "name": "Alpha Emlak & City CRM",
        "file": "Alpha_Emlak_Sunum_Mobil.html",
        "subject": "Şehrin Hakimi Olun: Emlak Sektöründe Yapay Zeka Devrimi",
        "body": """
        Sayın Meslektaşım,
        
        Emlakçılık artık sadece "ilan asmak" değil, "doğru veriye sahip olmak" demektir. Bölgenizdeki her hareketi, her fiyat değişimini rakiplerinizden önce bilmek ister misiniz?
        
        <b>Alpha City CRM</b> ile tanışın:
        
        🗺️ <b>Canlı Bölge Hakimiyeti:</b> Harita üzerinde tüm portföyünüz ve potansiyel fırsatlar.
        🤝 <b>Yapay Zeka Eşleşmesi:</b> Müşteriniz "3+1 arıyorum" dediği an, sistem en uygun daireyi önüne getirir.
        📈 <b>Otomatik Değerleme:</b> "Bu ev ne kadar eder?" sorusuna verilerle cevap verin.
        
        Portföyünüzü cebinizde taşıyın, ofise hapsolmayın.
        
        Detaylı sunum dosyanız ekte hazırdır.
        
        <br>
        <div style="background-color: #f8f9fa; border-left: 4px solid #2980b9; padding: 10px; margin-top: 15px; font-style: italic;">
        <b>💡 SINIRLARI KALDIRIN</b><br>
        Mevcut emlak programları size yetmiyor mu?<br>
        Alpha Craft Intelligence, hayalinizdeki o "keşke olsa" dediğiniz sistemi sizin için sıfırdan inşa edebilir.<br>
        Bizimle vizyonunuzu paylaşın, gerisini yapay zekaya bırakın.
        </div>
        """
    },
    "staff": {
        "name": "Alpha Staff v2 (Personel)",
        "file": "Alpha_Staff_Sunum_Mobil.html",
        "subject": "Personel Yönetiminde Kaos Bitti: Otonom İK Sistemi",
        "body": """
        Sayın Yönetici,
        
        Vardiya çizelgeleri, izin karmaşası ve maaş günü stresi... Bu manuel süreçler size her ay kaç saate ve ne kadar paraya mal oluyor?
        
        <b>Alpha Staff v2</b> ile işletmenizi otopilota alın:
        
        👁️ <b>Yüz Tanıma & GPS:</b> "Kartımı evde unuttum" bahanesi tarih oldu.
        📅 <b>Akıllı Vardiya:</b> Sistem, personelinizin performansına ve yasal sınırlara göre en adil vardiyayı hazırlar.
        💰 <b>Tek Tıkla Bordro:</b> Ay sonu hesaplamaları saniyeler sürer.
        
        Personeliniz işine odaklansın, gerisini Alpha Staff halletsin.
        Kurulum detayları ekteki dosdadır.
        
        <br>
        <div style="background-color: #f8f9fa; border-left: 4px solid #27ae60; padding: 10px; margin-top: 15px; font-style: italic;">
        <b>💡 SİZE ÖZEL ÇÖZÜMLER</b><br>
        Fabrikanız veya ofisiniz için standartların dışında bir takip sistemi mi gerekiyor?<br>
        Biz, her işletmenin DNA'sına uygun <b>özel yazılım çözümleri</b> geliştiriyoruz.<br>
        Probleminiz ne kadar karmaşıksa, çözümümüz o kadar etkili olur.
        </div>
        """
    },
     "invest": {
        "name": "Alpha Craft Yatırımcı Sunumu",
        "file": "Alpha_Yatirim_Sunum_Mobil.html",
        "subject": "Davet: Geleceğin Unicorn'una Erken Erişim Fırsatı",
        "body": """
        Merhaba,
        
        Dünya değişiyor. İş yapış şekilleri, yapay zeka ve otomasyon ile yeniden yazılıyor. Biz bu değişimi izlemiyor, <b>onu yönetiyoruz.</b>
        
        <b>Alpha Craft Intelligence (AZI)</b> olarak; Stok, CRM ve Personel yönetimini tek bir "Yapay Zeka Beyni" altında birleştirdik.
        
        🚀 <b>Neden Alpha Craft?</b>
        - Hazır ve çalışan ürün ailesi.
        - Kanıtlanmış gelir modeli (SaaS).
        - Ölçeklenebilir, küresel vizyon.
        
        Büyüme hikayemize ortak olmanız için hazırladığımız özel yatırımcı sunumunu ekte bilgilerinize sunarım.
        
        Saygılarımla,
        """
    }
}

def get_presentation_content(product_key):
    """
    İlgili ürünün konu, metin ve dosya yolunu döner.
    """
    prod = PRODUCTS.get(product_key)
    if not prod:
        return None
    
    file_path = os.path.join(PRESENTATION_DIR, prod["file"])
    
    # Dosya kontrolü
    attachments = []
    if os.path.exists(file_path):
        attachments.append(file_path)
    else:
        print(f"MARKETING WARNING: Sunum dosyası bulunamadı: {file_path}")
        
    return {
        "subject": prod["subject"],
        "body": prod["body"],
        "attachments": attachments,
        "product_name": prod["name"]
    }
