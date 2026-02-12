import os
import shutil

def check_and_copy():
    base_dir = r"C:\Users\alpay\.gemini\antigravity\scratch\alpha_emlak_pro"
    test_dest = r"C:\Users\alpay\.gemini\antigravity\scratch\test_copy"
    
    files = ["AlphaCraft_Satilik.xlsx", "AlphaCraft_Kiralik.xlsx"]
    
    print(f"Checking directory: {base_dir}")
    if not os.path.exists(base_dir):
        print("ERROR: Directory not found!")
        return

    os.makedirs(test_dest, exist_ok=True)
    
    all_files = os.listdir(base_dir)
    print(f"All files in dir: {all_files}")
    
    for f in files:
        src = os.path.join(base_dir, f)
        if os.path.exists(src):
            print(f"FOUND: {f}")
            try:
                dst = os.path.join(test_dest, f)
                shutil.copy2(src, dst)
                print(f"SUCCESS: Copied {f} to {test_dest}")
            except Exception as e:
                print(f"FAILURE: Could not copy {f}. Error: {e}")
        else:
            print(f"MISSING: {f} NOT FOUND in {base_dir}")

check_and_copy()
