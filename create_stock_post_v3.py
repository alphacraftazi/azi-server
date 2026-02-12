from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import glob
import textwrap

def create_stock_post_v3(bg_path, screenshot_path, logo_path, output_path):
    try:
        # Load Background
        bg = Image.open(bg_path).convert("RGBA")
        
        # Load Screenshot
        shot = Image.open(screenshot_path).convert("RGBA")
        
        # Load Logo
        logo = Image.open(logo_path).convert("RGBA")

        # Resize Background to standard post size if needed (e.g., 1080x1080 or keep original)
        # Assuming generated background is high res, let's work on that canvas
        bg_w, bg_h = bg.size
        draw = ImageDraw.Draw(bg)
        
        # --- 1. HEADER (Mimicking App Interface) ---
        # User said "copy logo and text same way as top left of interface"
        # We will create a "Header Bar" area
        header_y_start = 80
        
        # Logo
        logo_w = 100
        logo_aspect = logo.size[1] / logo.size[0]
        logo_h = int(logo_w * logo_aspect)
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        header_x = 80
        bg.paste(logo, (header_x, header_y_start), mask=logo)
        
        # Title "ALPHA STOCK" - Mimicing app font style (Clean, Bold, White)
        try:
            # Roboto or Arial
            header_font = ImageFont.truetype("arialbd.ttf", 70) 
            body_font = ImageFont.truetype("arial.ttf", 36)
            highlight_font = ImageFont.truetype("arialbd.ttf", 38)
            footer_font = ImageFont.truetype("ariali.ttf", 35)
        except:
            header_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            highlight_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()

        draw.text((header_x + logo_w + 30, header_y_start + 10), "ALPHA STOCK", font=header_font, fill=(255, 255, 255))
        
        # --- 2. SCREENSHOT (Hero) ---
        # Placed below header
        
        target_shot_w = int(bg_w * 0.85)
        shot_ratio = shot.size[1] / shot.size[0]
        target_shot_h = int(target_shot_w * shot_ratio)
        
        # Crop screenshot top bar if it duplicates our header? 
        # User said "copy logo and text", implies maybe we use the screenshot header?
        # But also said "copy... and put it". Let's assume we reconstructed it above.
        # So we display the FULL screenshot below, creating a "monitor" effect.
        
        shot = shot.resize((target_shot_w, target_shot_h), Image.Resampling.LANCZOS)
        
        shot_x = (bg_w - target_shot_w) // 2
        shot_y = header_y_start + 150
        
        # Shadow/Glow (Subtle Blue)
        shadow = Image.new("RGBA", (target_shot_w + 60, target_shot_h + 60), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([0, 0, target_shot_w + 60, target_shot_h + 60], fill=(0, 100, 255, 80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(30))
        
        bg.paste(shadow, (shot_x - 30, shot_y - 30), mask=shadow)
        bg.paste(shot, (shot_x, shot_y))
        
        # --- 3. RICH TEXT CONTENT (Metaphorical & Sincere) ---
        # "Abartabilirsin, merak uyandır, samimi ve mecazi"
        
        text_area_y = shot_y + target_shot_h + 60
        text_x = 80
        max_width = bg_w - 160
        
        # Headline
        headline = "Deponuzun nefes aldığını hissettiniz mi?"
        draw.text((text_x, text_area_y), headline, font=highlight_font, fill=(0, 243, 255))
        
        # Body Text
        body_text_lines = [
            "Raflarınızdaki o sessiz kutular artık konuşmaya başladı.",
            "Siz uyurken stoklarınızı sayan, 'Ben bitiyorum!' diye fısıldayan,",
            "zarar eden ürünü gözünden tanıyan bir dijital bekçi düşünün.",
            "",
            "Excel tablolarında boğulmak mı? O devir kapandı.",
            "Alpha Stock, işletmenizin görünmeyen kahramanı olmaya geldi."
        ]
        
        current_text_y = text_area_y + 60
        for line in body_text_lines:
            if line == "":
                current_text_y += 20
                continue
            
            # Wrap if needed (though these lines are short enough for wide image)
            draw.text((text_x, current_text_y), line, font=body_font, fill=(220, 220, 220))
            current_text_y += 50

        # --- 4. FOOTER ---
        footer_text = "ARTIK KOLAY"
        f_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
        f_w = f_bbox[2] - f_bbox[0]
        f_x = (bg_w - f_w) // 2
        f_y = bg_h - 100
        
        # Line above footer
        draw.line((f_x - 50, f_y - 20, f_x + f_w + 50, f_y - 20), fill=(188, 19, 254), width=1)
        draw.text((f_x, f_y), footer_text, font=footer_font, fill=(200, 200, 200))

        # Save
        bg.save(output_path)
        print(f"Generated Stock Post V3: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

# --- EXECUTION BLOCK ---
base_dir = r"C:\Users\alpay\.gemini\antigravity\brain\f22e87e4-7ff6-4c52-9680-f3881ca466f0"
app_dir = r"c:\Users\alpay\.gemini\antigravity\scratch\azi_app"

logo_file = os.path.join(app_dir, "logo-box-a.png")
screenshot_file = os.path.join(app_dir, "shot_stock_list.png")

# Find latest background
def get_latest_file(pattern):
    files = glob.glob(os.path.join(base_dir, pattern))
    if files:
        return max(files, key=os.path.getctime)
    return None

bg_file = get_latest_file("bg_simple_dark_luxury*")

if bg_file and os.path.exists(screenshot_file) and os.path.exists(logo_file):
    output_file = os.path.join(base_dir, "post_stock_showcase_v3.png")
    create_stock_post_v3(bg_file, screenshot_file, logo_file, output_file)
else:
    print(f"Missing files.\nBG: {bg_file}\nShot: {screenshot_file}\nLogo: {logo_file}")
