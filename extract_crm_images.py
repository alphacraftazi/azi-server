
import os
import re
import base64

SOURCE_FILE = r"c:\Users\alpay\.gemini\antigravity\scratch\Alpha_Sunumlar_TekDosya\Alpha_Emlak_Sunum_Mobil.html"
DEST_DIR = r"c:\Users\alpay\.gemini\antigravity\scratch\alphacraft_website\assets"

def extract_all_images():
    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Regex for all base64 images
        matches = re.finditer(r'src="data:image/png;base64,([^"]+)"', content)
        
        for i, match in enumerate(matches):
            b64_data = match.group(1)
            img_data = base64.b64decode(b64_data)
            
            output_name = f"crm_extracted_{i}.png"
            output_path = os.path.join(DEST_DIR, output_name)
            
            with open(output_path, "wb") as out_f:
                out_f.write(img_data)
            print(f"Extracted {output_name} ({len(img_data)} bytes)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_all_images()
