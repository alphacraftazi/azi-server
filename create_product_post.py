from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import glob
import textwrap

def create_product_post(bg_path, screenshot_path, logo_path, output_path):
    try:
        # Load Background
        bg = Image.open(bg_path).convert("RGBA")
        bg_w, bg_h = bg.size
        
        # Load Screenshot
        shot = Image.open(screenshot_path).convert("RGBA")
        
        # Load Logo
        logo = Image.open(logo_path).convert("RGBA")

        draw = ImageDraw.Draw(bg)
        
        # --- 1. PLACE SCREENSHOT (CENTERED) ---
        # Target size for the screenshot (e.g., 70% of background width)
        target_w = int(bg_w * 0.75)
        aspect = shot.size[1] / shot.size[0]
        target_h = int(target_w * aspect)
        
        shot = shot.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # Center coordinates
        shot_x = (bg_w - target_w) // 2
        shot_y = (bg_h - target_h) // 2 + 50 # Slightly pushed down to leave room for title
        
        # Add Glow/Shadow behind screenshot
        shadow_offset = 15
        shadow = Image.new("RGBA", (target_w + 40, target_h + 40), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rectangle([0, 0, target_w + 40, target_h + 40], fill=(0, 243, 255, 100)) # Cyan glow
        shadow = shadow.filter(ImageFilter.GaussianBlur(15))
        
        bg.paste(shadow, (shot_x - 20, shot_y - 20), mask=shadow)
        bg.paste(shot, (shot_x, shot_y))
        
        # Draw Border around screenshot
        draw.rectangle([shot_x, shot_y, shot_x + target_w, shot_y + target_h], outline=(255, 255, 255), width=3)

        # --- 2. LOGO PLACEMENT (Top Right) ---
        logo_w = int(bg_w * 0.15)
        logo_aspect = logo.size[1] / logo.size[0]
        logo_h = int(logo_w * logo_aspect)
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        pad = 50
        bg.paste(logo, (bg_w - logo_w - pad, pad), mask=logo)

        # --- 3. TEXT OVERLAY ---
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 90)
            subtitle_font = ImageFont.truetype("arial.ttf", 40)
            footer_font = ImageFont.truetype("ariali.ttf", 35)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()
            
        # Title "ALPHA STOCK" centered top
        title_text = "ALPHA STOCK"
        
        # Calculate text balance centered
        # bbox is (left, top, right, bottom)
        bbox = draw.textbbox((0, 0), title_text, font=title_font)
        text_w = bbox[2] - bbox[0]
        title_x = (bg_w - text_w) // 2
        title_y = 60
        
        # Draw Title with Shadow
        draw.text((title_x + 4, title_y + 4), title_text, font=title_font, fill=(0, 0, 0))
        draw.text((title_x, title_y), title_text, font=title_font, fill=(255, 255, 255))
        
        # Subtitle "Yapay Zeka Destekli Stok Yönetimi"
        sub_text = "Yapay Zeka Destekli Stok Yönetimi"
        bbox_sub = draw.textbbox((0, 0), sub_text, font=subtitle_font)
        sub_w = bbox_sub[2] - bbox_sub[0]
        sub_x = (bg_w - sub_w) // 2
        sub_y = title_y + 110
        
        draw.text((sub_x, sub_y), sub_text, font=subtitle_font, fill=(0, 243, 255)) # Cyan

        # --- 4. FLOATING BADGES (Optional) ---
        # Let's add simple badges at the bottom corners of the screenshot
        badges = ["Anlık Takip", "Maliyet Analizi", "Otomatik Sipariş"]
        badge_y = shot_y + target_h + 30
        badge_start_x = shot_x
        
        for badge in badges:
            # Draw badge background
            # Approx width per badge
            badge_font = subtitle_font
            b_bbox = draw.textbbox((0, 0), badge, font=badge_font)
            b_w = b_bbox[2] - b_bbox[0] + 40
            b_h = b_bbox[3] - b_bbox[1] + 20
            
            # Draw semi-transparent box
            shape = [(badge_start_x, badge_y), (badge_start_x + b_w, badge_y + b_h)]
            overlay = Image.new('RGBA', bg.size, (0,0,0,0))
            d_over = ImageDraw.Draw(overlay)
            d_over.rounded_rectangle(shape, radius=15, fill=(188, 19, 254, 200)) # Purple
            bg = Image.alpha_composite(bg, overlay)
            draw = ImageDraw.Draw(bg)
            
            # Text
            draw.text((badge_start_x + 20, badge_y + 5), badge, font=badge_font, fill=(255, 255, 255))
            
            badge_start_x += b_w + 30

        # --- 5. FOOTER ---
        footer_text = "ARTIK KOLAY"
        f_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
        f_w = f_bbox[2] - f_bbox[0]
        f_x = (bg_w - f_w) // 2
        f_y = bg_h - 80
        
        draw.line((f_x - 50, f_y - 20, f_x + f_w + 50, f_y - 20), fill=(188, 19, 254), width=1)
        draw.text((f_x, f_y), footer_text, font=footer_font, fill=(200, 200, 200))

        # Save
        bg.save(output_path)
        print(f"Generated Product Post: {output_path}")

    except Exception as e:
        print(f"Error: {e}")

# --- EXECUTION BLOCK ---
base_dir = r"C:\Users\alpay\.gemini\antigravity\brain\f22e87e4-7ff6-4c52-9680-f3881ca466f0"
app_dir = r"c:\Users\alpay\.gemini\antigravity\scratch\azi_app"

logo_file = os.path.join(base_dir, "uploaded_media_1769804178537.png")
screenshot_file = os.path.join(app_dir, "shot_stock_list.png")

# Find latest background
def get_latest_file(pattern):
    files = glob.glob(os.path.join(base_dir, pattern))
    if files:
        return max(files, key=os.path.getctime)
    return None

bg_file = get_latest_file("bg_product_showcase*")

if bg_file and os.path.exists(screenshot_file):
    output_file = os.path.join(base_dir, "post_product_showcase.png")
    create_product_post(bg_file, screenshot_file, logo_file, output_file)
else:
    print(f"Missing files. BG: {bg_file}, Shot: {screenshot_file}")
