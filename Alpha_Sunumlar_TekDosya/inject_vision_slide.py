import os
import re

# The specific HTML content for the new slide
# Note: Exact whitespace matching for removal might be tricky, so we will use a marker-based removal.
SLIDE_MARKER_START = "<!-- GELECEĞİN DEVRİMİ SLİDE -->"
SLIDE_HTML = """
            <!-- GELECEĞİN DEVRİMİ SLİDE -->
            <section data-background-color="#020617">
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
                    <div style="margin-bottom: 20px;">
                       <i class="fa-solid fa-rocket" style="font-size: 60px; color: #f59e0b; text-shadow: 0 0 20px rgba(245, 158, 11, 0.6);"></i>
                    </div>
                    <h2 style="font-family: 'Orbitron', sans-serif; font-size: 1.8em; color: #f8fafc; text-transform: uppercase; margin-bottom: 20px; letter-spacing: 2px;">
                        GELECEĞİN DEVRİMİ
                    </h2>
                    <div class="feature-box" style="border-left: 4px solid #f59e0b; background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 10px; text-align: left;">
                        <p style="font-size: 0.9em; line-height: 1.6; color: #e2e8f0; margin-bottom: 15px;">
                            <strong style="color: #f59e0b;">Sadece devlerin değil, herkesin hakkı.</strong><br>
                            Yapay zeka artık bir lüks değil, zorunluluktur. Alpha Craft olarak vizyonumuz; mahalle esnafından KOBİ'lere kadar her ölçekteki işletmeyi <strong>Yapay Zeka</strong> gücüyle donatmaktır.
                        </p>
                        <p style="font-size: 0.9em; line-height: 1.6; color: #cbd5e1;">
                            Küçük işletmenin çevikliğini, büyük verinin gücüyle birleştiriyoruz. Operasyonel yükünüzü sıfıra indirin, veriye dayalı kararlar alın ve geleceğin teknolojisine <strong>bugünden</strong> erişin.
                        </p>
                    </div>
                </div>
            </section>
"""

files_to_update = [
    "Alpha_Emlak_Sunum_Mobil.html",
    "Alpha_Genel_Musteri_Sunumu.html",
    "Alpha_Staff_Sunum_Mobil.html",
    "Alpha_Stock_Sunum_Mobil.html",
    "Alpha_Yatirim_Sunum_Mobil.html",
    "ac_class.html"
]

base_dir = r"C:\Users\alpay\.gemini\antigravity\scratch\Alpha_Sunumlar_TekDosya"

def remove_existing_slide(content):
    """
    Removes the slide if it exists. 
    It looks for the marker and tries to find the matching closing </section>.
    Because we might have injected it partially or oddly, we rely on the specific content structure we added.
    Our added content has a single <section>...</section> block.
    """
    if SLIDE_MARKER_START not in content:
        return content
    
    # Simple strategy: The added slide is a known block.
    # We will try to remove the exact block we added first.
    # If indentation varies, this literal replace fails.
    # So we use a regex or string manipulation.
    
    start_idx = content.find(SLIDE_MARKER_START)
    if start_idx == -1: return content
    
    # We expect a <section ...> after the marker
    section_start = content.find("<section", start_idx)
    if section_start == -1: return content # Should not happen if marker is there
    
    # Find the closing </section> for this specific slide.
    # Since our slide doesn't have nested sections, the first </section> after section_start should be it.
    section_end = content.find("</section>", section_start)
    if section_end == -1: return content
    
    cutoff = section_end + len("</section>")
    
    print("  Found existing slide, removing...")
    return content[:start_idx] + content[cutoff:]

def find_first_root_slide_end(content):
    """
    Finds the index after the closing </section> of the FIRST root-level slide.
    Handles nested <section> tags by counting depth.
    """
    slides_div = '<div class="slides">'
    start_search = content.find(slides_div)
    if start_search == -1:
        return -1
    
    start_search += len(slides_div)
    
    # Find first <section
    first_section = content.find("<section", start_search)
    if first_section == -1:
        return -1
        
    # Now walk through looking for <section and </section> to balance
    depth = 0
    i = first_section
    
    # A crude parser
    while i < len(content):
        # Look for next tag start
        next_tag_open = content.find("<section", i)
        next_tag_close = content.find("</section>", i)
        
        if next_tag_close == -1:
            return -1 # Malformed
            
        # Determine which comes first
        if next_tag_open != -1 and next_tag_open < next_tag_close:
            # We found a nested section opening
            depth += 1
            i = next_tag_open + 1 # Move past to avoid infinite loop
        else:
            # We found a closing tag
            depth -= 1
            i = next_tag_close + len("</section>")
            
            if depth == 0:
                # We closed the root section
                return i
                
    return -1

def process_files():
    for filename in files_to_update:
        filepath = os.path.join(base_dir, filename)
        if not os.path.exists(filepath):
            print(f"Skipping {filename}: Not found.")
            continue
            
        print(f"Processing {filename}...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 1. Clean up
            clean_content = remove_existing_slide(content)
            
            # 2. Find insertion point
            insert_pos = find_first_root_slide_end(clean_content)
            
            if insert_pos == -1:
                print(f"  Warning: Could not find end of first slide in {filename}. Appending to slides div start.")
                # Fallback: Insert at start of slides div
                slides_pos = clean_content.find('<div class="slides">')
                if slides_pos != -1:
                    insert_pos = slides_pos + len('<div class="slides">')
                else:
                    print("  Error: No slides div found. Skipping.")
                    continue
            
            # 3. Inject
            final_content = clean_content[:insert_pos] + "\n" + SLIDE_HTML + clean_content[insert_pos:]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(final_content)
                
            print(f"  Updated successfully.")
            
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    process_files()
