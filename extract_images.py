
import os
import re
import base64

SOURCE_DIR = r"c:\Users\alpay\.gemini\antigravity\scratch\Alpha_Sunumlar_TekDosya"
DEST_DIR = r"c:\Users\alpay\.gemini\antigravity\scratch\alphacraft_website\assets"

files_to_process = {
    "Alpha_Stock_Sunum_Mobil.html": "stock_dashboard_real.png",
    "Alpha_Staff_Sunum_Mobil.html": "staff_dashboard_real.png",
    "Alpha_Emlak_Sunum_Mobil.html": "crm_dashboard_real.png",
    "ac_class.html": "class_dashboard_real.png"
}

def extract_first_base64_image(html_path, output_name):
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Regex to find data:image/png;base64,.....
        # We look for the first occurrence which is usually the main dashboard screenshot in these templates
        match = re.search(r'src="data:image/png;base64,([^"]+)"', content)
        if match:
            b64_data = match.group(1)
            img_data = base64.b64decode(b64_data)
            
            output_path = os.path.join(DEST_DIR, output_name)
            with open(output_path, "wb") as out_f:
                out_f.write(img_data)
            print(f"Extracted {output_name} from {os.path.basename(html_path)}")
        else:
            print(f"No base64 image found in {os.path.basename(html_path)}")

    except Exception as e:
        print(f"Error processing {html_path}: {e}")

if __name__ == "__main__":
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
        
    for filename, output_name in files_to_process.items():
        extract_first_base64_image(os.path.join(SOURCE_DIR, filename), output_name)
