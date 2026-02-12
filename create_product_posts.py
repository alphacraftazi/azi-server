import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_product_post(screenshot_path, product_suffix, highlight_color, subtitle, bullets, output_path):
    try:
        # Canvas Settings
        W, H = 1080, 1080
        img = Image.new('RGBA', (W, H), (10, 10, 20)) # Dark background
        draw = ImageDraw.Draw(img)

        # --- 1. BACKGROUND ---
        # Subtle glow
        glow = Image.new('RGBA', (W, H), (0,0,0,0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse((200, 200, 880, 880), fill=(20, 30, 60, 100))
        glow = glow.filter(ImageFilter.GaussianBlur(100))
        img = Image.alpha_composite(img, glow)
        draw = ImageDraw.Draw(img) # Refresh draw

        # --- 2. HEADER (UI STYLE) ---
        # Structure: [Box A]  ALPHA CRAFT  [PRODUCT]
        
        try:
            brand_font = ImageFont.truetype("arialbd.ttf", 55)    # ALPHA CRAFT
            product_font = ImageFont.truetype("arialbd.ttf", 45)  # STOCK (Smaller)
            logo_font = ImageFont.truetype("arialbd.ttf", 40)     # "A" inside box
            subtitle_font = ImageFont.truetype("arial.ttf", 30)
            bullet_header_font = ImageFont.truetype("arialbd.ttf", 26) 
            bullet_body_font = ImageFont.truetype("ariali.ttf", 26)   
        except:
            brand_font = ImageFont.load_default()
            product_font = ImageFont.load_default()
            logo_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            bullet_header_font = ImageFont.load_default()
            bullet_body_font = ImageFont.load_default()

        # 2.1 Draw Logo Box "A"
        box_s = 70
        
        txt_brand = "ALPHA CRAFT"
        w_brand = draw.textlength(txt_brand, font=brand_font)
        w_product = draw.textlength(product_suffix, font=product_font)
        gap = 20
        total_header_w = box_s + gap + w_brand + gap + w_product
        
        start_x = (W - total_header_w) / 2
        header_y = 60
        
        # Draw Box
        box_x = start_x
        box_y = header_y
        draw.rectangle([box_x, box_y, box_x + box_s, box_y + box_s], outline=highlight_color, width=3, fill=(0, 60, 70))
        
        # Draw "A"
        w_a = draw.textlength("A", font=logo_font)
        draw.text((box_x + (box_s - w_a)/2, box_y + 10), "A", font=logo_font, fill=highlight_color)
        
        # Draw "ALPHA CRAFT"
        text_x = box_x + box_s + gap
        draw.text((text_x, header_y + 5), txt_brand, font=brand_font, fill=(255, 255, 255))
        
        # Draw Product Suffix (Colored, Smaller)
        text_x += w_brand + gap
        draw.text((text_x, header_y + 12), product_suffix, font=product_font, fill=highlight_color)

        # Subtitle
        subtitle_w = draw.textlength(subtitle, font=subtitle_font)
        draw.text(((W - subtitle_w) / 2, 150), subtitle, font=subtitle_font, fill=(200, 200, 200))

        # --- 3. SCREENSHOT ---
        if os.path.exists(screenshot_path):
            ss = Image.open(screenshot_path).convert("RGBA")
            # Resize
            max_w = 850
            max_h = 450
            
            ss_ratio = ss.size[0] / ss.size[1]
            target_w = max_w
            target_h = int(target_w / ss_ratio)
            
            if target_h > max_h:
                target_h = max_h
                target_w = int(target_h * ss_ratio)
            
            ss = ss.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            ss_x = (W - target_w) // 2
            ss_y = 200 
            
            # Shadow
            draw.rectangle([ss_x+15, ss_y+15, ss_x+target_w+15, ss_y+target_h+15], fill=(0,0,0,150))
            # Paste
            img.paste(ss, (ss_x, ss_y), mask=ss)
            # Border
            draw.rectangle([ss_x, ss_y, ss_x+target_w, ss_y+target_h], outline=highlight_color, width=2)
            
            content_start_y = ss_y + target_h + 50
        else:
            content_start_y = 400

        # --- 4. DETAILS ---
        sector_heading = bullets[0]
        remaining_bullets = bullets[1:]
        
        current_y = content_start_y
        
        # Draw Sector Heading
        try:
             sector_font = ImageFont.truetype("arialbd.ttf", 36)
        except:
             sector_font = ImageFont.load_default()
             
        heading_w = draw.textlength(sector_heading, font=sector_font)
        draw.text(((W - heading_w) / 2, current_y), sector_heading, font=sector_font, fill=(255, 255, 255))
        
        current_y += 70 
        
        text_x = 70
        
        for item in remaining_bullets:
            draw.ellipse((text_x, current_y + 8, text_x + 10, current_y + 18), fill=highlight_color)
            
            if "/" in item:
                feature, scenario = item.split("/", 1)
                feature = feature.strip()
                scenario = scenario.strip()
            else:
                feature = item
                scenario = ""
            
            draw.text((text_x + 30, current_y), feature, font=bullet_header_font, fill=highlight_color)
            
            current_y += 32
            draw.text((text_x + 30, current_y), f"\"{scenario}\"", font=bullet_body_font, fill=(230, 230, 230))
            current_y += 45

        # Img Save
        img.save(output_path)
        print(f"Generated: {output_path}")

    except Exception as e:
        print(f"Error creating post {output_path}: {e}")

def create_azi_post(screenshot_path, logo_path, output_path):
    try:
        # Canvas
        W, H = 1080, 1080
        # Cinematic Void Background (Deep Blue-Black)
        img = Image.new('RGBA', (W, H), (2, 2, 10))
        draw = ImageDraw.Draw(img)
        
        # --- 1. ATMOSPHERE (Cinematic Glows) ---
        # Instead of a grid, let's do a soft "Event Horizon" glow
        glow = Image.new('RGBA', (W, H), (0,0,0,0))
        glow_draw = ImageDraw.Draw(glow)
        
        # Bottom-Right Blue Haze
        glow_draw.ellipse((400, 600, 1400, 1400), fill=(0, 20, 60, 60))
        # Top-Left Purple Haze
        glow_draw.ellipse((-300, -300, 600, 600), fill=(30, 0, 60, 40))
        
        # Central Core Glow (Behind Logo/Brain)
        glow_draw.ellipse((300, 300, 780, 780), fill=(0, 100, 255, 30))
        
        glow = glow.filter(ImageFilter.GaussianBlur(150))
        img = Image.alpha_composite(img, glow)
        
        # --- 2. BACKGROUND VISUAL (The "Brain" Texture) ---
        if os.path.exists(screenshot_path):
            # This is the 'azi_ai_concept.png'
            bg_vis = Image.open(screenshot_path).convert("RGBA")
            # Make it cover the screen but very subtle/blended
            bg_vis = bg_vis.resize((W, H), Image.Resampling.LANCZOS)
            
            # Mask to fade it out at edges
            mask = Image.new('L', (W, H), 0)
            m_draw = ImageDraw.Draw(mask)
            # Center visible, edges fade
            m_draw.ellipse((100, 100, 980, 980), fill=80) # Low opacity (80/255)
            mask = mask.filter(ImageFilter.GaussianBlur(100))
            
            # Apply color tint? Let's keep original but low opacity
            bg_vis.putalpha(mask)
            img = Image.alpha_composite(img, bg_vis)

        # --- 3. HERO LOGO (The "Core") ---
        # The user wanted their logo. Let's make it the central "Eye" or "Chip"
        draw = ImageDraw.Draw(img) # Refresh
        
        if os.path.exists(logo_path):
             logo = Image.open(logo_path).convert("RGBA")
             # Size: Medium-Large, commanding presence
             logo_w = 280
             aspect = logo.size[1] / logo.size[0]
             logo_h = int(logo_w * aspect)
             logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
             
             logo_x = (W - logo_w) // 2
             logo_y = 380 # Center Vertical area
             
             # intense Glow behind logo (Cyber Blue)
             lglow = Image.new('RGBA', (W, H), (0,0,0,0))
             lg_draw = ImageDraw.Draw(lglow)
             # Inner bright glow
             lg_draw.ellipse((logo_x-20, logo_y-20, logo_x+logo_w+20, logo_y+logo_h+20), fill=(0, 150, 255, 100))
             # Outer soft glow
             lg_draw.ellipse((logo_x-100, logo_y-100, logo_x+logo_w+100, logo_y+logo_h+100), fill=(0, 50, 200, 40))
             
             lglow = lglow.filter(ImageFilter.GaussianBlur(50))
             img = Image.alpha_composite(img, lglow)
             
             img.paste(logo, (logo_x, logo_y), mask=logo)
             draw = ImageDraw.Draw(img) # Refresh

        # --- 4. TYPOGRAPHY (Minimalist, Impactful) ---
        try:
            # Use 'arial.ttf' for thin/clean look, 'arialbd.ttf' for bold
            q_font = ImageFont.truetype("arial.ttf", 36)
            a_font = ImageFont.truetype("arialbd.ttf", 70)
            tag_font = ImageFont.truetype("arialbd.ttf", 55)
        except:
            q_font = ImageFont.load_default()
            a_font = ImageFont.load_default()
            tag_font = ImageFont.load_default()

        # 1. QUESTION (Top, Floating)
        # "SORUNUN MU VAR?" - Clean, spaced, White
        q_text = "SORUNUN MU VAR?"
        q_w = draw.textlength(q_text, font=q_font)
        draw.text(((W - q_w)/2, 280), q_text, font=q_font, fill=(200, 220, 255))
        
        # 2. ANSWER (Below Logo)
        # "BEN BURADAYIM." - Strong, reliable
        a_text = "BEN BURADAYIM."
        a_w = draw.textlength(a_text, font=a_font)
        a_y = 700
        
        # Subtle glow text
        for off in range(1, 4):
            draw.text(( (W-a_w)/2 + off, a_y + off), a_text, font=a_font, fill=(0, 50, 100)) # Drop Shadow
            
        draw.text(((W - a_w)/2, a_y), a_text, font=a_font, fill=(255, 255, 255))
        
        # 3. TAGLINE (Bottom)
        # "ARTIK KOLAY" - The Promise. Blue/Cyan.
        tag_text = "ARTIK KOLAY"
        tag_w = draw.textlength(tag_text, font=tag_font)
        draw.text(((W - tag_w)/2, 820), tag_text, font=tag_font, fill=(59, 130, 246)) # Brand Blue

        img.save(output_path)
        print(f"Generated Cinematic AZI Post: {output_path}")

    except Exception as e:
        print(f"Error creating AZI post: {e}")

# --- CONFIGURATION ---
base_dir = r"C:\Users\alpay\.gemini\antigravity\scratch"
brain_dir = r"C:\Users\alpay\.gemini\antigravity\brain\73f2b249-ba00-4335-afc0-41d72f98baa2"
website_assets = os.path.join(base_dir, "alphacraft_website", "assets")

products = [
    {
        "name": "stock",
        "suffix": "STOCK",
        "color": (59, 130, 246),
        "subtitle": "ARTIK KOLAY",
        "screenshot": "stock_dashboard_real.png",
        "bullets": [
            "KAFELER VE RESTORANLAR İÇİN DİJİTAL BEYİN",
            "Anlık Karlılık Analizi / San Sebastian maliyetiniz %12 arttı, menü fiyatını güncellemeyi unutmayın.",
            "Kritik Stok Uyarısı / Haftasonuna girmeden Espresso çekirdekleri bitmek üzere, sipariş oluşturuldu.",
            "Kaçak ve Fire Takibi / Dün akşamki sayımda 2 litre süt eksik çıktı, kamera kaydına bakın.",
            "Akıllı Tedarik / Un fiyatları haftaya artabilir, şimdiden stok yapmanız öneriliyor."
        ]
    },
    {
        "name": "emlak",
        "suffix": "EMLAK",
        "color": (34, 197, 94),
        "subtitle": "ARTIK KOLAY",
        "screenshot": "crm_dashboard_real.png",
        "bullets": [
            "EMLAKÇILAR İÇİN SATIŞ KAPATAN ASİSTAN",
            "Akıllı Müşteri Eşleştirme / Portföye yeni eklenen 3+1 daire, Mehmet Bey'in kriterlerine uyuyor.",
            "Bölge Fiyat Analizi / Batıkent bölgesinde kiralar %20 arttı, mülk sahibini bilgilendirin.",
            "Potansiyel Müşteri / Bu ilanı en çok 'Çocuklu Aileler' görüntülüyor, pazarlamayı buna göre yapın.",
            "Dijital Arşiv / Ayşe Hanım'ın tapu fotokopisi eksik, SMS ile talep edildi."
        ]
    },
    {
        "name": "staff",
        "suffix": "STAFF",
        "color": (239, 68, 68),
        "subtitle": "ARTIK KOLAY",
        "screenshot": "staff_dashboard_real.png",
        "bullets": [
            "PERSONEL YÖNETİMİNDE OTONOM DÖNEM",
            "QR ile Hızlı Giriş / Personel kartı unutma derdi bitti, cepten okutup mesaiye başladılar.",
            "Vardiya Planlama / Bu haftasonu yoğunluk bekleniyor, 2 garson daha mesaiye gelmeli.",
            "Saha Takibi / Saha ekibiniz rotadan saptı, konum kontrol ediliyor.",
            "Maaş Hesabı / Ayşe'nin fazla mesaisi yasal sınırı aştı, sistem otomatik uyarı verdi."
        ]
    },
    {
        "name": "class",
        "suffix": "CLASS",
        "color": (245, 158, 11),
        "subtitle": "ARTIK KOLAY",
        "screenshot": "class_dashboard_real.png",
        "bullets": [
            "OKULLAR İÇİN HATASIZ YÖNETİM",
            "Devamsızlık Takibi / Can bugün derse gelmedi, velisini arayıp bilgi verin.",
            "Sınıf Karlılığı / 10-A sınıfının mevcudu çok düştü, sınıf şuan zarar ediyor. Kayıt aksiyonu alın.",
            "Risk Analizi / Efe'nin devamsızlığı sınıra yaklaştı, veli görüşmesi ayarlayın.",
            "Kapasite Verimliliği / Boş geçen sınıflar ve çakışan dersler size her ay %10 zarar ettiriyor."
        ]
    }
]

# Create AZI Post
azi_ss_path = os.path.join(website_assets, "azi_ai_concept.png")
azi_out_path = os.path.join(brain_dir, "post_azi_final.png")
azi_logo_path = os.path.join(brain_dir, "uploaded_media_1769895114486.png")
create_azi_post(azi_ss_path, azi_logo_path, azi_out_path)

for p in products:
    ss_path = os.path.join(website_assets, p["screenshot"])
    out_path = os.path.join(brain_dir, f"post_product_{p['name']}_v5.png")
    # create_product_post(ss_path, p["suffix"], p["color"], p["subtitle"], p["bullets"], out_path)
    pass
