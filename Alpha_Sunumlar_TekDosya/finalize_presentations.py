import os
import re

# Base directory
base_dir = r"C:\Users\alpay\.gemini\antigravity\scratch\Alpha_Sunumlar_TekDosya"
artifacts_dir = r"C:\Users\alpay\.gemini\antigravity\brain\8f035aa4-4ce2-4b8b-8a81-476cecab8359"

# File paths
staff_file = os.path.join(base_dir, "Alpha_Staff_Sunum_Mobil.html")
investment_file = os.path.join(base_dir, "Alpha_Yatirim_Sunum_Mobil.html")
general_file = os.path.join(base_dir, "Alpha_Genel_Musteri_Sunumu.html")
stock_file = os.path.join(base_dir, "Alpha_Stock_Sunum_Mobil.html")

# Screenshot Paths (Relative to artifacts dir, but we will use absolute paths for the browser/presentation)
# Ideally, we should copy these to a local 'assets' folder if deploying, but for now we link to the artifacts.
# Since the HTMLs are in scratch, and artifacts are in brain, we'll use the absolute path or a relative path if possible.
# Given the user's setup, absolute paths are safer for local viewing.
def get_artifact_path(filename):
    return f"{artifacts_dir}\\{filename}".replace("\\", "/")

staff_screenshot = get_artifact_path("ac_staff_screenshots_1769102862343.webp")
estate_screenshot = get_artifact_path("ac_emlak_refine_screenshots_1769104331410.webp")
stock_screenshot = get_artifact_path("ac_stock_screenshots_1769101295924.webp")
# For investment, we can use a generic one or the estate one as it's the "Main" product often
investment_screenshot = estate_screenshot 

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated: {path}")

def inject_slide(content, slide_html):
    # Inject before the last closing section or at the end of slides
    if "</section>\n            </div>" in content:
        return content.replace("</section>\n            </div>", f"</section>\n\n            {slide_html}\n            </div>")
    elif "</div>\n    </div>" in content:
         # Reveal.js standard closing
        return content.replace("</div>\n    </div>", f"{slide_html}\n        </div>\n    </div>")
    else:
        print("Warning: Could not find injection point for slide.")
        return content

# -------------------------------------------------------------------------
# 1. Update Staff Presentation
# -------------------------------------------------------------------------
print("Processing Staff Presentation...")
staff_content = read_file(staff_file)

# Fix Logo "S" to "A"
# Look for <div ...>S</div> inside logo-box or similar structure
# Based on previous context, it might be <span ...>S</span> or just text inside a div
# Regex to find S inside the logo box div
staff_content = re.sub(r'(<div[^>]*class="[^"]*logo-box[^"]*"[^>]*>\s*)S(\s*</div>)', r'\1A\2', staff_content)
# Also try specific style if class isn't used exactly like that
staff_content = re.sub(r'(<div[^>]*style="[^"]*background:\s*var\(--brand-blue\)[^"]*"[^>]*>\s*<span[^>]*>\s*)S(\s*</span>\s*</div>)', r'\1A\2', staff_content)

# Add Screenshot Slide
staff_slide = f"""
            <!-- INTERFACE DETAIL SLIDE -->
            <section>
                <h3 style="color: var(--brand-blue); text-transform: uppercase;">Arayüz Detayları</h3>
                <div style="display: flex; justify-content: center; align-items: center; margin-top: 20px;">
                    <img src="{staff_screenshot}" style="max-height: 500px; border-radius: 15px; box-shadow: 0 0 30px rgba(14, 165, 233, 0.3);" alt="Staff Interface">
                </div>
                <p style="font-size: 0.6em; color: #94a3b8; margin-top: 15px;">Personel Yönetim Paneli - Detaylı Görünüm</p>
            </section>
"""
staff_content = inject_slide(staff_content, staff_slide)
write_file(staff_file, staff_content)


# -------------------------------------------------------------------------
# 2. Update Investment Presentation
# -------------------------------------------------------------------------
print("Processing Investment Presentation...")
inv_content = read_file(investment_file)

# Remove Animated Background
inv_content = re.sub(r'\.particles\s*\{[^}]*\}', '', inv_content) # CSS class
inv_content = re.sub(r'@keyframes\s+move-bg\s*\{[^}]*\}', '', inv_content) # CSS Keyframes
inv_content = re.sub(r'<div\s+class="particles">\s*</div>', '', inv_content) # HTML Element

# Add Screenshot Slide
inv_slide = f"""
            <!-- INTERFACE DETAIL SLIDE -->
            <section>
                <h3 style="color: var(--brand-purple); text-transform: uppercase;">Ekosistem Arayüzü</h3>
                <div style="display: flex; justify-content: center; align-items: center; margin-top: 20px;">
                    <img src="{investment_screenshot}" style="max-height: 500px; border-radius: 15px; box-shadow: 0 0 30px rgba(139, 92, 246, 0.3);" alt="Ecosystem Interface">
                </div>
                <p style="font-size: 0.6em; color: #94a3b8; margin-top: 15px;">Alpha Craft Dijital Ekosistem Paneli</p>
            </section>
"""
inv_content = inject_slide(inv_content, inv_slide)
write_file(investment_file, inv_content)


# -------------------------------------------------------------------------
# 3. Update General/Estate Presentation
# -------------------------------------------------------------------------
print("Processing General Presentation...")
gen_content = read_file(general_file)

# Update Text: "Users ask questions" -> "AZI proactively notifies"
# Finding the specific text block. It might be in Turkish: "Kullanıcılar soru sorar..."
# We will look for "soru sorar" or similar and replace the block.
# Assuming the text is something like "Kullanıcılar AZI’ye soru sorabilir..."
# Replacement: "AZI kullanıcılara proaktif bildirimler ve öneriler gönderir."

# Regex for the specific list item or paragraph regarding AZI interaction
# Pattern: looking for "soru sorar" or "soru sorabilir"
gen_content = re.sub(r'(Kullanıcılar\s+AZI.{0,20}\s+soru\s+sorar)', r'AZI kullanıcılara proaktif bildirimler ve öneriler gönderir', gen_content, flags=re.IGNORECASE)
gen_content = re.sub(r'(Sadece\s+bir\s+chatbot\s+değildir)', r'Sadece cevap veren bir chatbot değildir, inisiyatif alır.', gen_content, flags=re.IGNORECASE)


# Add Screenshot Slide
gen_slide = f"""
            <!-- INTERFACE DETAIL SLIDE -->
            <section>
                <h3 style="color: var(--brand-green); text-transform: uppercase;">Emlak Yönetim Paneli</h3>
                <div style="display: flex; justify-content: center; align-items: center; margin-top: 20px;">
                    <img src="{estate_screenshot}" style="max-height: 500px; border-radius: 15px; box-shadow: 0 0 30px rgba(16, 185, 129, 0.3);" alt="Estate Interface">
                </div>
                <p style="font-size: 0.6em; color: #94a3b8; margin-top: 15px;">Detaylı Portföy ve Müşteri Yönetimi</p>
            </section>
"""
gen_content = inject_slide(gen_content, gen_slide)
write_file(general_file, gen_content)


# -------------------------------------------------------------------------
# 4. Update Stock Presentation
# -------------------------------------------------------------------------
print("Processing Stock Presentation...")
stock_content = read_file(stock_file)

# Add Screenshot Slide
stock_slide = f"""
            <!-- INTERFACE DETAIL SLIDE -->
            <section>
                <h3 style="color: #f59e0b; text-transform: uppercase;">Stok Takip Paneli</h3>
                <div style="display: flex; justify-content: center; align-items: center; margin-top: 20px;">
                    <img src="{stock_screenshot}" style="max-height: 500px; border-radius: 15px; box-shadow: 0 0 30px rgba(245, 158, 11, 0.3);" alt="Stock Interface">
                </div>
                <p style="font-size: 0.6em; color: #94a3b8; margin-top: 15px;">Akıllı Stok ve Maliyet Analizi</p>
            </section>
"""
stock_content = inject_slide(stock_content, stock_slide)
write_file(stock_file, stock_content)

print("All presentations updated successfully.")
