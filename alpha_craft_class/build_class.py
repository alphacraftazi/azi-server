import PyInstaller.__main__
import os
import shutil

# 1. Temizlik
if os.path.exists("dist"): shutil.rmtree("dist")
if os.path.exists("build"): shutil.rmtree("build")

# 2. Build Konfigürasyonu
print("Building Alpha Class Tracking...")

PyInstaller.__main__.run([
    'main_cloud_tracking.py',     # Ana dosya
    '--name=AlphaClass',          # Exe adı
    '--onefile',                  # Tek dosya modu
    '--noconsole',                # Konsol penceresi açılmasın
    '--add-data=index_class_tracking.html;.', # HTML dosyasını dahil et
    '--clean',                    # Cache temizle
    '--log-level=WARN'
])

print("\n------------------------------------------------")
print("Build Tamamlandı! 'dist/AlphaClass.exe' dosyasına bakınız.")
print("------------------------------------------------")
