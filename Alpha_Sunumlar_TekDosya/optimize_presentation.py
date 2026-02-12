
import base64
import os
import io
from PIL import Image
import re

html_path = 'ac_class.html'
max_width_px = 600

def resize_base64_img(b64_str):
    try:
        img_data = base64.b64decode(b64_str)
        img = Image.open(io.BytesIO(img_data))
        
        if img.width > max_width_px:
            ratio = max_width_px / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width_px, new_height), Image.Resampling.LANCZOS)
            
            buf = io.BytesIO()
            img.save(buf, format='PNG', optimize=True)
            new_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            print(f"Resized image from {img.width} to {max_width_px} width.")
            return new_b64
        return b64_str
    except Exception as e:
        print(f"Error checking/resizing base64: {e}")
        return b64_str

print(f"Reading {html_path}...")
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Regular expression to find base64 data URIs
# Pattern: data:image/png;base64,....."
# We need to capture the base64 part.
# NOTE: This is heavy regex for a large file, but strictly finding "data:image/png;base64,([A-Za-z0-9+/=]+)" should work if chunks aren't broken.
# However, modifying string while regexing is tricky.

# Better approach: Split by "data:image/png;base64,"
parts = content.split('data:image/png;base64,')
new_content = parts[0]

for i in range(1, len(parts)):
    part = parts[i]
    # Find the end of quote
    end_quote_idx = part.find('"') 
    if end_quote_idx == -1:
        # Fallback if single quote or no quote (css url)
        end_quote_idx = part.find("'")
    
    if end_quote_idx != -1:
        b64_data = part[:end_quote_idx]
        rest = part[end_quote_idx:]
        
        # Resize
        new_b64 = resize_base64_img(b64_data)
        
        new_content += 'data:image/png;base64,' + new_b64 + rest
    else:
        # Could not identify end, just append (safeguard)
        new_content += 'data:image/png;base64,' + part

# CSS FIXES
# 1. Ensure .screenshot-frame doesn't have restrictive max-width on mobile.
# We will inject a style tag at the end of head.
style_fix = """
    <style>
        img { max-width: 100% !important; height: auto !important; }
        .screenshot-frame { max-width: 95% !important; width: 95% !important; }
        .slides section { height: 100% !important; overflow-y: auto !important; }
    </style>
</head>
"""

# Replace </head> with our fix + </head>
if '<style>' in style_fix and '</head>' in new_content:
   new_content = new_content.replace('</head>', style_fix)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Saved optimized {html_path}")
