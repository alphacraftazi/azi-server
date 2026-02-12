import os
import re
import base64
import mimetypes

# Config
SOURCE_DIR = r"C:\Users\alpay\.gemini\antigravity\brain\8f035aa4-4ce2-4b8b-8a81-476cecab8359"
DEST_DIR = r"C:\Users\alpay\.gemini\antigravity\scratch\Alpha_Sunumlar_TekDosya"
HTML_FILES = [
    ("ac_staff_presentation.html", "Alpha_Staff_Sunum_Mobil.html"), 
    ("ac_emlak_presentation.html", "Alpha_Emlak_Sunum_Mobil.html"),
    ("ac_stock_presentation.html", "Alpha_Stock_Sunum_Mobil.html"),
    ("alpha_craft_presentation.html", "Alpha_Yatirim_Sunum_Mobil.html"),
    ("alpha_craft_general_presentation.html", "Alpha_Genel_Musteri_Sunumu.html")
]

def setup_dirs():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
    print(f"Destination: {DEST_DIR}")

def get_base64_image(path):
    mime_type, _ = mimetypes.guess_type(path)
    if not mime_type:
        mime_type = 'image/png'
    
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
    return f"data:{mime_type};base64,{encoded_string}"

def process_file(filename, output_name):
    src_path = os.path.join(SOURCE_DIR, filename)
    if not os.path.exists(src_path):
        print(f"File not found: {src_path}")
        return

    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find ANY image in src attributes
    pattern = r'src=["\']([^"\']+\.(?:png|jpg|jpeg|webp))["\']'
    
    def replace_match(match):
        raw_path = match.group(1)
        
        # 1. Clean path
        clean_path = raw_path.replace('file:///', '')
        import urllib.parse
        clean_path = urllib.parse.unquote(clean_path)
        
        # 2. Determine Absolute Source Path
        if os.path.isabs(clean_path):
             src_abs_path = os.path.normpath(clean_path)
        else:
             src_abs_path = os.path.join(SOURCE_DIR, os.path.normpath(clean_path))

        # 3. Check existence with Fuzzy Matching (Timestamp support)
        if not os.path.exists(src_abs_path):
            basename = os.path.basename(clean_path)
            name_part, ext_part = os.path.splitext(basename)
            candidates = [f for f in os.listdir(SOURCE_DIR) if f.startswith(name_part) and f.endswith(ext_part)]
            
            if candidates:
                best_match = sorted(candidates)[-1]
                src_abs_path = os.path.join(SOURCE_DIR, best_match)
                print(f"Resolved {basename} -> {best_match}")
            else:
                # Try fallback
                fallback_path = os.path.join(SOURCE_DIR, basename)
                if os.path.exists(fallback_path):
                    src_abs_path = fallback_path
                else:
                    print(f"Warning: Image not found: {src_abs_path}")
                    return match.group(0) 

        # 4. Embed as Base64
        try:
            base64_data = get_base64_image(src_abs_path)
            # Shorten log output
            print(f"Embedded: {os.path.basename(src_abs_path)}")
            return f'src="{base64_data}"'
        except Exception as e:
            print(f"Error encoding {src_abs_path}: {e}")
            return match.group(0)

    new_content = re.sub(pattern, replace_match, content)

    # Save to dest
    dest_path = os.path.join(DEST_DIR, output_name)
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Saved Standalone: {dest_path}")

def main():
    setup_dirs()
    for input_file, output_name in HTML_FILES:
        process_file(input_file, output_name)
    print("Embedding Complete.")

if __name__ == "__main__":
    main()
