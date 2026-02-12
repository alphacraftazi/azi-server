@echo off
title Alpha Craft Prototip 2 - KRITIK HATA COZUMU (GUNCEL 6)
color 0a
cls

echo ======================================================
echo Alpha Craft Staff Prototip 2 - KRITIK DERLEME BAŞLADI
echo (Bu islem dinamik DLL hatalarini gidermeyi hedefler.)
echo ======================================================
echo.

:: KRİTİK: Çalışma Dizinini Scriptin Olduğu Yere Ayarla
cd /d "%~dp0"

echo [1/4] Eski dosyalar temizleniyor...
:: Yalnızca geçici build klasörü ve spec dosyaları siliniyor.
rmdir /s /q build 2>nul
del /f /q AlphaCraft_Prototip2.spec 2>nul
del /f /q *.spec 2>nul

echo.
echo [2/4] PyInstaller Komutu Hazirlaniyor...
set PYINSTALLER_CMD=python -m PyInstaller

echo.
echo [3/4] Yeni surum derleniyor (main_pro2.py)...
:: KRİTİK ÇÖZÜM: Simge dosyası bulunamadı (FileNotFoundError) hatası çözüldü.
:: Eksik olan simge dosyası (--icon) komut satırından kaldırıldı.
%PYINSTALLER_CMD% --noconfirm --windowed --name "AlphaCraft_Prototip2" ^
--add-data "index_pro2.html;." ^
--collect-all PyQt5 ^
--collect-all webview ^
--hidden-import "PyQt5.Qt" ^
--hidden-import "PyQt5.QtCore" ^
--hidden-import "PyQt5.QtGui" main_pro2.py

echo.
echo [4/4] Islem Tamamlandi!
echo.
:: Hata kontrolü (hala --onedir modunda)
if exist "C:\AlphaCraftPro2\dist\AlphaCraft_Prototip2\AlphaCraft_Prototip2.exe" (
echo BASARILI: EXE dosyasi olusturuldu.
echo Lütfen dist klasörüne gidin ve AlphaCraft_Prototip2 klasörü icindeki EXE dosyasini calistirin.
) else (
echo HATA: EXE dosyasi olusturulamadi veya Build islemi basarisiz oldu.
echo Lütfen yukaridaki konsol ciktilarini inceleyin.
)
echo.
pause