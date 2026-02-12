import base64
import os
import re
from PIL import Image
import io

html_path = 'ac_class.html'
img1_path = 'dashboard_real_v2.png'
img2_path = 'azi_ai_concept.png'

def resize_and_encode(path, max_width=800):
    if not os.path.exists(path):
        return None
    
    try:
        with Image.open(path) as img:
            # Resize if needed
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                print(f"Resized {path} to {max_width}x{new_height}")
            
            # Save to buffer
            buf = io.BytesIO()
            img.save(buf, format='PNG', optimize=True)
            return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
    except Exception as e:
        print(f"Error processing {path}: {e}")
        return None

print(f"Processing {html_path}...")

with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Image 1: Dashboard
# Previously replaced data:... string might be huge.
# We look for the <img> tag structure or just replace the src attribute if we can identify it.
# Strategy: Re-replace the *placeholder* texts if I can, OR specific context.
# Since the file HAS base64 now, I should search for the Base64 pattern.

# However, regexing 1MB strings is slow/risky.
# Better: Look for unique context BEFORE the image tag.

# Context 1: <!-- Updated Image: Real user screenshot v2 (Placeholder) -->
# followed by <img src="..."
# We will regenerate the WHOLE <img> tag.

b64_1 = resize_and_encode(img1_path)
if b64_1:
    # Regex to find the first img tag after the comment
    pattern1 = r'(<!-- Updated Image: Real user screenshot v2 \(Placeholder\) -->\s*<img src=")[^"]+(" class="screenshot-img">)'
    # Note: The file content might have been formatted. Let's be flexible.
    # Actually, simpler: Find the comment, then find the next closing >?
    # Let's simple check if we can replace the previous large chunk.
    # Since we know the previous script output, we can try to locate the src attribute.
    
    # Alternative: The user might have reverted content? No.
    # Let's Assume the previous state is active.
    
    # We will construct a new HTML snippet including style.
    new_tag1 = f'<img src="{b64_1}" class="screenshot-img" style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">'
    
    # Find the block
    start_marker = '<!-- Updated Image: Real user screenshot v2 (Placeholder) -->'
    end_marker = 'class="screenshot-img">'
    
    idx = html_content.find(start_marker)
    if idx != -1:
        # Find the end of the img tag
        tag_end = html_content.find('>', idx + len(start_marker))
        if tag_end != -1:
            # Replace the whole range
            # Carefull: existing tag is <img src="..." class="screenshot-img">
            # We want to replace from <img ... to >
            
            # Let's try to match strictly string replacement if possible, but the base64 is variable.
            # Best way: split by the marker, take pre, find end of img tag in post.
            pre = html_content[:idx + len(start_marker)]
            post = html_content[idx + len(start_marker):]
            
            # post starts with typically \s*<img ... >
            img_start = post.find('<img')
            img_end = post.find('>', img_start) + 1
            
            if img_start != -1 and img_end != -1:
                html_content = pre + post[:img_start] + new_tag1 + post[img_end:]
                print("Updated Image 1 with responsive style.")

# Image 2: AZI Concept
# Context: <!-- Using explicit path for images -->
# <img src="..."
b64_2 = resize_and_encode(img2_path)
if b64_2:
    start_marker2 = '<!-- Using explicit path for images -->'
    
    new_tag2 = f'<img src="{b64_2}" style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); object-fit: contain;">'
    
    idx = html_content.find(start_marker2)
    if idx != -1:
        pre = html_content[:idx + len(start_marker2)]
        post = html_content[idx + len(start_marker2):]
        
        img_start = post.find('<img')
        img_end = post.find('>', img_start) + 1
        
        if img_start != -1 and img_end != -1:
            html_content = pre + post[:img_start] + new_tag2 + post[img_end:]
            print("Updated Image 2 with responsive style.")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML file updated.")
