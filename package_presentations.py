import os
import re
import shutil

# Config
SOURCE_DIR = r"C:\Users\alpay\.gemini\antigravity\brain\8f035aa4-4ce2-4b8b-8a81-476cecab8359"
DEST_DIR = r"C:\Users\alpay\.gemini\antigravity\scratch\Alpha_Sunumlar"
HTML_FILES = ["ac_staff_presentation.html", "ac_emlak_presentation.html", "ac_stock_presentation.html"]

def setup_dirs():
    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)
    os.makedirs(DEST_DIR)
    os.makedirs(os.path.join(DEST_DIR, "assets"))
    print(f"Created directory: {DEST_DIR}")

def process_file(filename):
    src_path = os.path.join(SOURCE_DIR, filename)
    if not os.path.exists(src_path):
        print(f"File not found: {src_path}")
        return

    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find ANY image in src attributes
    # Covers: file:///..., C:/..., or just "image.png"
    pattern = r'src=["\']([^"\']+\.(?:png|jpg|jpeg|webp))["\']'
    
    def replace_match(match):
        raw_path = match.group(1)
        
        # 1. Clean path
        clean_path = raw_path.replace('file:///', '')
        import urllib.parse
        clean_path = urllib.parse.unquote(clean_path)
        
        # 2. Determine Absolute Source Path
        if os.path.isabs(clean_path):
             # It's already absolute (e.g. C:/Users/...)
             src_abs_path = os.path.normpath(clean_path)
        else:
             # It's relative (e.g. "image.png"), assume it's in SOURCE_DIR
             src_abs_path = os.path.join(SOURCE_DIR, os.path.normpath(clean_path))

        # 3. Check existence
        if not os.path.exists(src_abs_path):
            # Try finding it directly in SOURCE_DIR by basename (fallback)
            basename = os.path.basename(clean_path)
            
            # Check for timestamped versions (e.g. shot_hunter_123.png)
            name_part, ext_part = os.path.splitext(basename)
            candidates = [f for f in os.listdir(SOURCE_DIR) if f.startswith(name_part) and f.endswith(ext_part)]
            
            if candidates:
                # Take the most recent one or first match
                best_match = sorted(candidates)[-1] # lexical sort usually puts higher timestamps last or just pick one
                src_abs_path = os.path.join(SOURCE_DIR, best_match)
                print(f"Resolved {basename} -> {best_match}")
            else:
                # Try fallback path without timestamp checking
                fallback_path = os.path.join(SOURCE_DIR, basename)
                if os.path.exists(fallback_path):
                    src_abs_path = fallback_path
                else:
                    print(f"Warning: Image not found: {src_abs_path}")
                    return match.group(0) # Keep original

        # 4. Copy file
        basename = os.path.basename(src_abs_path)
        dest_path = os.path.join(DEST_DIR, "assets", basename)
        shutil.copy2(src_abs_path, dest_path)
        
        return f'src="assets/{basename}"'

    new_content = re.sub(pattern, replace_match, content)

    # Save to dest
    dest_html = os.path.join(DEST_DIR, filename)
    with open(dest_html, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Processed {filename} -> Saved to {dest_html}")

def main():
    setup_dirs()
    for html in HTML_FILES:
        process_file(html)
    print("Packaging Complete.")

if __name__ == "__main__":
    main()
