import base64
import os

html_path = 'ac_class.html'
img1_path = 'dashboard_real_v2.png'
img2_path = 'azi_ai_concept.png'

print(f"Processing {html_path}...")

# Read HTML
try:
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
except FileNotFoundError:
    print(f"Error: {html_path} not found.")
    exit(1)

# Encode Image 1 (Dashboard)
if os.path.exists(img1_path):
    print(f"Encoding {img1_path}...")
    with open(img1_path, 'rb') as f:
        img1_b64 = base64.b64encode(f.read()).decode('utf-8')
        img1_src = f"data:image/png;base64,{img1_b64}"
    
    # Target 1: The dashboard placeholder URL
    target1 = 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1600&q=80'
    if target1 in html_content:
        html_content = html_content.replace(target1, img1_src)
        print("Replaced Dashboard image URL.")
    else:
        print("Warning: Dashboard URL target not found in HTML.")
else:
    print(f"Warning: {img1_path} not found. Skipping.")

# Encode Image 2 (AZI Concept)
if os.path.exists(img2_path):
    print(f"Encoding {img2_path}...")
    with open(img2_path, 'rb') as f:
        img2_b64 = base64.b64encode(f.read()).decode('utf-8')
        img2_src = f"data:image/png;base64,{img2_b64}"
    
    # Target 2: The AZI concept placeholder URL
    target2 = 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=1000&q=80'
    if target2 in html_content:
        html_content = html_content.replace(target2, img2_src)
        print("Replaced AZI Concept image URL.")
    else:
        print("Warning: AZI Concept URL target not found in HTML.")
else:
    print(f"Warning: {img2_path} not found. Skipping.")

# Save
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML file updated with embedded Base64 images.")
