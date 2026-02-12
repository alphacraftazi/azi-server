
import shutil
import os

SOURCE_DIR = r"c:\Users\alpay\.gemini\antigravity\scratch\alphacraft_website"
OUTPUT_FILENAME = r"c:\Users\alpay\.gemini\antigravity\scratch\alphacraft_website_deploy"

def zip_website():
    try:
        shutil.make_archive(OUTPUT_FILENAME, 'zip', SOURCE_DIR)
        print(f"Website zipped successfully to {OUTPUT_FILENAME}.zip")
    except Exception as e:
        print(f"Error zipping website: {e}")

if __name__ == "__main__":
    zip_website()
