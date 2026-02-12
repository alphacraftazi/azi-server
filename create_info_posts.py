import textwrap
import os
from PIL import Image, ImageDraw, ImageFont

def create_info_post(bg_path, logo_path, title_text, bullet_points, output_path):
    try:
        # Load images
        img = Image.open(bg_path).convert("RGBA")
        logo = Image.open(logo_path).convert("RGBA")
        
        width, height = img.size
        
        # --- LAYOUT SETTINGS ---
        panel_ratio = 0.53 # Panel covers 53% of width
        panel_width = int(width * panel_ratio)
        padding_left = 60
        max_text_width_px = panel_width - (padding_left * 2)
        
        # --- DARK OVERLAY FOR READABILITY ---
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        # Draw a dark box behind the text area
        draw_overlay.rectangle([(0, 0), (panel_width, height)], fill=(0, 0, 0, 200)) 
        
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

        # --- LOGO PLACEMENT (Top Right) ---
        logo_w = int(width * 0.15)
        aspect = logo.size[1] / logo.size[0]
        logo_h = int(logo_w * aspect)
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        pad = 50
        img.paste(logo, (width - logo_w - pad, pad), mask=logo)
        
        # --- FONTS ---
        try:
            # Resized fonts for better fit
            title_font = ImageFont.truetype("arialbd.ttf", 65)
            body_font = ImageFont.truetype("arial.ttf", 35)
            footer_font = ImageFont.truetype("ariali.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()

        # --- TEXT CONTENT ---
        text_x = padding_left
        start_y = 100 # Moved up from 150
        
        # Draw Title
        title_lines = title_text.count('\n') + 1
        line_height = 70
        
        draw.text((text_x + 3, start_y + 3), title_text, font=title_font, fill=(0, 0, 0))
        draw.text((text_x, start_y), title_text, font=title_font, fill=(0, 243, 255))
        
        # Draw Separator Line (Dynamic)
        line_y = start_y + (title_lines * line_height) + 20
        draw.line((text_x, line_y, text_x + 250, line_y), fill=(255, 255, 255), width=3)
        
        # Draw Bullet Points with Wrapping
        current_y = line_y + 40
        
        # Estimate chars per line based on font size and width (Safe approx for Arial 35)
        # 35px width is roughly 16-18px per char avg.
        chars_per_line = int(max_text_width_px / 18) 
        
        for point in bullet_points:
            # Bullet circle
            draw.ellipse((text_x, current_y + 12, text_x + 12, current_y + 24), fill=(188, 19, 254))
            
            # Wrap text
            wrapped_lines = textwrap.wrap(point, width=chars_per_line)
            
            for i, line in enumerate(wrapped_lines):
                draw.text((text_x + 35, current_y), line, font=body_font, fill=(255, 255, 255))
                current_y += 45 # Line height spacing
            
            current_y += 15 # Reduced extra space between items (was 20)

        # --- FOOTER SLOGAN ---
        slogan = "ARTIK KOLAY"
        footer_y = height - 100
        
        # Footer line
        draw.line((text_x, footer_y - 20, panel_width - 40, footer_y - 20), fill=(188, 19, 254), width=1)
        draw.text((text_x, footer_y), slogan, font=footer_font, fill=(200, 200, 200))

        # Save
        img.save(output_path)
        print(f"Generated: {output_path}")

    except Exception as e:
        print(f"Error processing {output_path}: {e}")

# Base Paths
base_dir = r"C:\Users\alpay\.gemini\antigravity\brain\f22e87e4-7ff6-4c52-9680-f3881ca466f0"
logo_file = os.path.join(base_dir, "uploaded_media_1769804178537.png")

import glob

def get_latest_file(pattern):
    files = glob.glob(os.path.join(base_dir, pattern))
    if files:
        return max(files, key=os.path.getctime)
    return None

# Get latest background images for the new specific topics
bg1 = get_latest_file("bg_post1_azi_intro*.png")
bg2 = get_latest_file("bg_post2_business_scale*.png")
bg3 = get_latest_file("bg_post3_alpha_vision*.png")

# --- POST 1: AZI KİMDİR? ---
if bg1:
    create_info_post(
        bg1,
        logo_file,
        "AZI KİMDİR?",
        [
            "İşletmenizin Dijital CEO'su",
            "7/24 Kesintisiz & Otonom Analiz",
            "Stok, Personel, Finans Tek Merkezde",
            "İnternetsiz Çalışan Güvenli Beyin",
            "Sizi Dinler, Öğrenir ve Uygular"
        ],
        os.path.join(base_dir, "post1_azi_final_v7.png")
    )
else:
    print("Error: BG1 (AZI) not found")

# --- POST 2: HER İŞLETME İÇİN (Universal Scalability) ---
if bg2:
    create_info_post(
        bg2,
        logo_file,
        "HER ÖLÇEĞE\nUYGUN", # Added newline for better fit
        [
            "Her Soruna Çözüm",
            "Küçükten Dev İşletmelere",
            "Kapasitenizle Büyüyen Yapı",
            "Sınır Tanımayan Entegrasyon",
            "Yapay Zeka Destekli Büyüme",
            "Size Özel Butik Mimariler"
        ],
        os.path.join(base_dir, "post2_scale_final_v7.png")
    )
else:
    print("Error: BG2 (Scale) not found")

# --- POST 3: ALPHA CRAFT VİZYONU (Vision) ---
if bg3:
    create_info_post(
        bg3,
        logo_file,
        "VİZYONUMUZ",
        [
            "Sadece Bir Yazılım Değil, İşletmenizin Dijital Omurgası",
            "Veri Odaklı Kararlarla Geleceğin Ticaretini Şekillendirin",
            "Analizden Yönetime Tam Otonom Yapay Zeka Devrimi",
            "Sınırları Aşan, Kendi Kendine Öğrenen Dijital Zeka"
        ],
        os.path.join(base_dir, "post3_vision_final_v7.png")
    )
else:
    print("Error: BG3 (Vision) not found")
