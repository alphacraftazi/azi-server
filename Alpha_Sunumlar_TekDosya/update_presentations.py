
import os
import re

# Base path
base_path = r'C:\Users\alpay\.gemini\antigravity\scratch\Alpha_Sunumlar_TekDosya'

# List of files to process for "FOUNDER" removal
files_to_update = [
    'Alpha_Genel_Musteri_Sunumu.html',
    'Alpha_Emlak_Sunum_Mobil.html',
    'Alpha_Stock_Sunum_Mobil.html',
    'Alpha_Staff_Sunum_Mobil.html',
    'Alpha_Yatirim_Sunum_Mobil.html',
    'ac_class.html'
]

# 1. REMOVE "FOUNDER" TITLE GLOBALLY
print("--- Starting Global FOUNDER Removal ---")
founder_pattern = re.compile(r'<div[^>]*>\s*FOUNDER\s*</div>', re.IGNORECASE)

for filename in files_to_update:
    filepath = os.path.join(base_path, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if founder_pattern.search(content):
            print(f"Found 'FOUNDER' in {filename}. Removing...")
            new_content = founder_pattern.sub('', content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filename}")
        else:
            print(f"No 'FOUNDER' tag found in {filename}")
    else:
        print(f"File not found: {filename}")

# 2. UPDATE STAFF PRESENTATION LOGO TO "A"
print("\n--- Updating Staff Presentation Logo ---")
staff_file = 'Alpha_Staff_Sunum_Mobil.html'
staff_path = os.path.join(base_path, staff_file)

if os.path.exists(staff_path):
    with open(staff_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # CSS for the "A" logo
    logo_css = """
        /* NEW A LOGO STYLES */
        .app-logo-container {
            width: 100px;
            height: 100px;
            background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); /* Red gradient for Staff */
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 15px 40px rgba(239, 68, 68, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin: 0 auto 20px auto;
        }
        .app-logo-text {
            font-family: 'Inter', sans-serif;
            font-size: 60px;
            font-weight: bold;
            color: white;
        }
    """
    
    # HTML for the "A" logo
    logo_html = """
        <div class="app-logo-container">
            <div class="app-logo-text">A</div>
        </div>
    """

    # Inject CSS
    if ".app-logo-container" not in content:
        content = content.replace("</style>", f"{logo_css}\n</style>")
        print("Injected Logo CSS into Staff Presentation.")

    # Find and execute the first slide's image logo (usually the cover logo)
    match = re.search(r'(<section[^>]*>)(.*?)<h1', content, re.DOTALL | re.IGNORECASE)
    if match:
        # Check if there is an image in this match block (the cover slide before heading)
        cover_content = match.group(2)
        if '<img' in cover_content:
            # Replace the image tag with our new logo div
            new_cover_content = re.sub(r'<img[^>]*>', logo_html, cover_content, count=1)
            content = content.replace(cover_content, new_cover_content)
            print("Replaced embedded logo image on cover slide with 'A' logo.")
        else:
            # If no image, prepend the logo to the h1
            content = re.sub(r'(<h1)', f'{logo_html}\n\\1', content, count=1)
            print("Prepended 'A' logo to H1 on cover slide.")
    
    with open(staff_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 3. FIX INVESTMENT PRESENTATION SCROLL
print("\n--- Fixing Investment Presentation Mobile Scroll ---")
invest_file = 'Alpha_Yatirim_Sunum_Mobil.html'
invest_path = os.path.join(base_path, invest_file)

if os.path.exists(invest_path):
    with open(invest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ensure touch is enabled in Reveal.initialize
    if 'touch: false' in content:
        content = content.replace('touch: false', 'touch: true')
        print("Enabled touch navigation in Reveal.js config.")
    
    # Ensure viewport allows scrolling/interaction
    if 'user-scalable=no' in content:
        content = content.replace('user-scalable=no', 'user-scalable=yes')
        print("Enabled user scaling in viewport.")

    # Fix potential CSS blocking
    css_fix = """
    <style>
        .reveal .controls { z-index: 9999 !important; }
        .reveal .progress { z-index: 9999 !important; }
        /* Ensure slides don't trap touch fully if not needed */
        .reveal .slides { pointer-events: none; }
        .reveal .slides section { pointer-events: auto; }
    </style>
    """
    if 'z-index: 9999' not in content:
        content = content.replace('</head>', f'{css_fix}\n</head>')
        print("Injected CSS fix for mobile controls.")

    with open(invest_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 4. SIMPLIFY GENERAL PRESENTATION FOR MOBILE
print("\n--- Simplifying General Presentation for Mobile ---")
general_file = 'Alpha_Genel_Musteri_Sunumu.html'
general_path = os.path.join(base_path, general_file)

if os.path.exists(general_path):
    with open(general_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Inject Media Queries for Mobile
    mobile_css = """
    <style>
        @media (max-width: 768px) {
            .cover-container {
                flex-direction: column !important;
                gap: 20px !important;
                text-align: center !important;
            }
            .cover-content {
                text-align: center !important;
            }
            .feature-grid {
                grid-template-columns: 1fr !important;
            }
            .module-grid {
                grid-template-columns: 1fr 1fr !important; /* 2 columns for modules on mobile */
            }
            .reveal h1 { font-size: 1.8em !important; }
            .reveal h2 { font-size: 1.3em !important; }
            .reveal p { font-size: 0.8em !important; }
            
            /* Hide complex visual elements on mobile to reduce clutter */
            .azi-glow { display: none !important; } 
            
            /* Stack flex containers */
            div[style*="display: flex"] {
                flex-direction: column !important;
                align-items: center !important;
                text-align: center !important;
            }
            /* Exception for small inline flex items if any, but general layout should stack */
        }
    </style>
    """
    
    if '@media (max-width: 768px)' not in content:
        content = content.replace('</head>', f'{mobile_css}\n</head>')
        print("Injected Mobile Responsive CSS into General Presentation.")
        
    with open(general_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("\n--- All Presentation Updates Completed ---")
