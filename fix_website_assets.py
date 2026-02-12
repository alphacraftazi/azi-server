import os
import shutil
import zipfile

# Source paths
base_dir = r"C:\Users\alpay\.gemini\antigravity\scratch"
website_dir = os.path.join(base_dir, "alphacraft_website")
assets_dir = os.path.join(website_dir, "assets")

# Image mappings (Source -> Destination Name in assets)
# Using the files we found earlier
image_map = {
    # Stock
    r"Alpha_Sunumlar\assets\shot_stock_list_1769101355467.png": "stock_dashboard_real.png",
    # Emlak
    r"Alpha_Sunumlar_TekDosya\shot_emlak_dashboard.png": "crm_dashboard_real.png",
    # Staff (Found in search results previously)
    r"Alpha_Sunumlar\assets\shot_staff_dashboard_1769102988381.png": "staff_dashboard_real.png",
    # Class (Using existing if valid, or a fallback if not found. Let's use azi_ai_concept as safe fallback or keep existing)
    # For now, let's keep existing class_dashboard_real.png if it has size, otherwise replace.
}

def verify_and_copy():
    print("Starting verification and copy...")
    
    # Ensure assets dir exists
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"Created {assets_dir}")

    # Process Copying
    for src_rel, dest_name in image_map.items():
        src_path = os.path.join(base_dir, src_rel)
        dest_path = os.path.join(assets_dir, dest_name)
        
        if os.path.exists(src_path):
            print(f"Copying {src_path} -> {dest_path}")
            shutil.copy2(src_path, dest_path)
        else:
            print(f"WARNING: Source not found: {src_path}")

    # Verify Class Dashboard exists, if not create dummy or copy fallback
    class_img = os.path.join(assets_dir, "class_dashboard_real.png")
    if not os.path.exists(class_img) or os.path.getsize(class_img) == 0:
        print("Class dashboard missing or empty. Using fallback.")
        # Fallback to AI concept
        fallback = os.path.join(base_dir, r"Alpha_Sunumlar_TekDosya\azi_ai_concept.png")
        if os.path.exists(fallback):
             shutil.copy2(fallback, class_img)
             print(f"Copied fallback for class: {fallback}")

    # List sizes
    print("\nCurrent Assets:")
    for f in os.listdir(assets_dir):
        fp = os.path.join(assets_dir, f)
        if os.path.isfile(fp):
             print(f"{f}: {os.path.getsize(fp)} bytes")

def create_zip():
    zip_path = os.path.join(base_dir, "alphacraft_website_deploy.zip")
    print(f"\nCreating zip at {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(website_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Archive name should be relative to website_dir for correct structure
                arcname = os.path.relpath(file_path, website_dir)
                # Force forward slashes for zip compatibility
                arcname = arcname.replace(os.path.sep, '/')
                
                print(f"Adding {arcname}")
                zipf.write(file_path, arcname)
    print("Zip created successfully.")

if __name__ == "__main__":
    verify_and_copy()
    create_zip()
