import os
import re

base_dir = r"C:\Users\alpay\.gemini\antigravity\scratch\Alpha_Sunumlar_TekDosya"
files = [
    "Alpha_Staff_Sunum_Mobil.html",
    "Alpha_Yatirim_Sunum_Mobil.html",
    "Alpha_Genel_Musteri_Sunumu.html",
    "Alpha_Stock_Sunum_Mobil.html"
]

def remove_duplicates(content):
    marker = '<!-- INTERFACE DETAIL SLIDE -->'
    parts = content.split(marker)
    
    if len(parts) <= 2:
        return content, False # 0 or 1 instace, no dupe
    
    print(f"Found {len(parts)-1} instances. Keeping the first one.")
    # Reconstruct: Part 0 + marker + Part 1. discard others if they are just the slide content?
    # This naive split might be dangerous if the marker is inside something else, but here it's a comment.
    # The slide content follows the marker.
    # We need to act carefully. 
    # Alternative: Remove the specific block if it appears twice with same content.
    
    # Better approach: Find the slide block via Regex and replace all occurrences with a single occurrence.
    # The slide block starts with <!-- INTERFACE DETAIL SLIDE --> and ends with </section>
    
    pattern = r'(<!-- INTERFACE DETAIL SLIDE -->\s*<section>.*?</section>)'
    
    # Find all matches
    matches = re.findall(pattern, content, flags=re.DOTALL)
    
    if len(matches) > 1:
        # Keep the first match only? Or replace the whole sequence of duplicates?
        # If they are adjacent (which they likely are due to append logic), we can just replace the repeated chunk.
        
        # Let's clean the file by removing ALL matches and appending ONE at the correct place?
        # Or just replace the *first* finding with itself, and remove subsequent findings.
        
        # safest:
        clean_content = re.sub(pattern, '', content, flags=re.DOTALL)
        # Now inject one back? No, we lost position.
        
        # Let's Iterate.
        new_content = content
        # We replace the *second* occurrence onwards with empty string?
        # But we need to be sure it's the *same* slide.
        
        # Since we just verified they are duplicates of the same injection:
        # We can locate the first match end index, and remove subsequent matches.
        
        first_match = re.search(pattern, content, flags=re.DOTALL)
        if first_match:
            # Output content up to end of first match
            valid_part = content[:first_match.end()]
            # Content after first match
            rest_part = content[first_match.end():]
            # Remove matches from rest_part
            rest_cleaned = re.sub(pattern, '', rest_part, flags=re.DOTALL)
            
            return valid_part + rest_cleaned, True
            
    return content, False

for fname in files:
    fpath = os.path.join(base_dir, fname)
    if not os.path.exists(fpath):
        print(f"Skipping {fname} (not found)")
        continue
        
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    new_content, changed = remove_duplicates(content)
    
    if changed:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"cleaned duplicates in {fname}")
    else:
        print(f"No duplicates found in {fname}")
