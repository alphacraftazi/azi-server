from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import glob

def create_stock_post_v2(bg_path, screenshot_path, logo_path, output_path):
    try:
        # Load Background
        bg = Image.open(bg_path).convert("RGBA")
        bg_w, bg_h = bg.size
        
        # Load Screenshot
        shot = Image.open(screenshot_path).convert("RGBA")
        
        # Load Correct Logo (Box A)
        logo = Image.open(logo_path).convert("RGBA")

        draw = ImageDraw.Draw(bg)
        
        # --- 1. LAYOUT CALCULATIONS ---
        # Margins
        top_margin = 150
        bottom_margin = 150
        side_margin = 80
        
        # Available height for screenshot
        # We want the screenshot to take up the middle bulk
        
        # --- 2. HEADER (Title + Logo) ---
        # Place Logo Top Left
        logo_target_w = 120
        logo_aspect = logo.size[1] / logo.size[0]
        logo_target_h = int(logo_target_w * logo_aspect)
        logo = logo.resize((logo_target_w, logo_target_h), Image.Resampling.LANCZOS)
        
        # Logo Position
        logo_x = side_margin
        logo_y = 60
        bg.paste(logo, (logo_x, logo_y), mask=logo)
        
        # Title "ALPHA STOCK" - Centered relative to screen width, or aligned with logo?
        # Let's Center the Title distinct from the logo
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 80)
            subtitle_font = ImageFont.truetype("arial.ttf", 40)
            footer_font = ImageFont.truetype("ariali.ttf", 35)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()

        title_text = "ALPHA STOCK"
        bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_w = bbox[2] - bbox[0]
        title_x = (bg_w - title_w) // 2
        # Align vertically with logo (approx)
        title_y = logo_y + (logo_target_h - (bbox[3]-bbox[1])) // 2 - 10 
        
        draw.text((title_x, title_y), title_text, font=title_font, fill=(255, 255, 255))
        
        # Subtitle under title
        sub_text = "Yapay Zeka Destekli Stok Yönetimi"
        s_bbox = draw.textbbox((0, 0), sub_text, font=subtitle_font)
        sub_w = s_bbox[2] - s_bbox[0]
        sub_x = (bg_w - sub_w) // 2
        sub_y = title_y + 90
        
        draw.text((sub_x, sub_y), sub_text, font=subtitle_font, fill=(0, 243, 255))

        # --- 3. SCREENSHOT PLACEMENT ---
        # Center the screenshot in the remaining space between Header and Footer
        
        # Footer is at bottom, let's say 120px from bottom
        footer_y_center = bg_h - 100
        header_bottom = sub_y + 60
        
        available_h = (footer_y_center - 80) - header_bottom
        available_w = bg_w - (side_margin * 2)
        
        # Resize screenshot to fit within available box while maintaining aspect ratio
        shot_ratio = shot.size[0] / shot.size[1]
        
        # Try to fit width first
        target_shot_w = int(available_w)
        target_shot_h = int(target_shot_w / shot_ratio)
        
        # If height is too big, fit to height
        if target_shot_h > available_h:
            target_shot_h = int(available_h)
            target_shot_w = int(target_shot_h * shot_ratio)
            
        shot_resized = shot.resize((target_shot_w, target_shot_h), Image.Resampling.LANCZOS)
        
        shot_x = (bg_w - target_shot_w) // 2
        shot_y = header_bottom + (available_h - target_shot_h) // 2
        
        # Shadow/Glow
        shadow = Image.new("RGBA", (target_shot_w + 40, target_shot_h + 40), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([0, 0, target_shot_w + 40, target_shot_h + 40], fill=(0, 0, 0, 150))
        shadow = shadow.filter(ImageFilter.GaussianBlur(20))
        
        bg.paste(shadow, (shot_x - 20, shot_y - 20), mask=shadow)
        
        # Paste Screenshot
        bg.paste(shot_resized, (shot_x, shot_y))
        
        # White Border
        draw.rectangle([shot_x, shot_y, shot_x + target_shot_w, shot_y + target_shot_h], outline=(255, 255, 255), width=2)
        
        # --- 4. FOOTER ---
        footer_text = "ARTIK KOLAY"
        f_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
        f_w = f_bbox[2] - f_bbox[0]
        f_x = (bg_w - f_w) // 2
        f_y = footer_y_center
        
        # Line above footer
        draw.line((f_x - 50, f_y - 20, f_x + f_w + 50, f_y - 20), fill=(188, 19, 254), width=1)
        draw.text((f_x, f_y), footer_text, font=footer_font, fill=(200, 200, 200))

        # Save
        bg.save(output_path)
        print(f"Generated Stock Post V2: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

# --- EXECUTION BLOCK ---
base_dir = r"C:\Users\alpay\.gemini\antigravity\brain\f22e87e4-7ff6-4c52-9680-f3881ca466f0"
app_dir = r"c:\Users\alpay\.gemini\antigravity\scratch\azi_app"

# Specific Requested Logo
logo_file = os.path.join(app_dir, "logo-box-a.png")
screenshot_file = os.path.join(app_dir, "shot_stock_list.png")

# Find latest background
def get_latest_file(pattern):
    files = glob.glob(os.path.join(base_dir, pattern))
    if files:
        return max(files, key=os.path.getctime)
    return None

bg_file = get_latest_file("bg_product_showcase*")

if bg_file and os.path.exists(screenshot_file) and os.path.exists(logo_file):
    output_file = os.path.join(base_dir, "post_stock_showcase_v2.png")
    create_stock_post_v2(bg_file, screenshot_file, logo_file, output_file)
else:
    print(f"Missing files.\nBG: {bg_file}\nShot: {screenshot_file}\nLogo: {logo_file}")
