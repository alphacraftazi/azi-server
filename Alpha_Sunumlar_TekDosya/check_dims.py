from PIL import Image
import os

img1_path = 'dashboard_real_v2.png'
img2_path = 'azi_ai_concept.png'

def check_dims(path):
    if os.path.exists(path):
        try:
            with Image.open(path) as img:
                print(f"{path}: {img.width}x{img.height}, Mode: {img.mode}")
        except Exception as e:
            print(f"Error reading {path}: {e}")
    else:
        print(f"{path} not found.")

check_dims(img1_path)
check_dims(img2_path)
