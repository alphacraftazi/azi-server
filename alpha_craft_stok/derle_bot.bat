@echo off
ECHO Alpha Craft Stock Masaüstü Uygulamasi Derleme Baslatiliyor...

:: Uygulamanin kaynak dosyasi (main.py)
SET SCRIPT_NAME=main.py

:: Uygulamanin ikonunu (istege bagli) ve pencere basligini belirle
SET APP_NAME=AlphaCraftStock

ECHO.
ECHO --- Derleme islemi baslatiliyor (index_stock.html dahil ediliyor) ---
ECHO.

:: KRİTİK DÜZELTME: --add-data komutu ile HTML dosyasini paketlemeye zorla.
:: Windows formatinda ayirici olarak noktalı virgül (;) kullanilir.
python -m PyInstaller --onefile --windowed --name %APP_NAME% --add-data "index_stock.html;." %SCRIPT_NAME%

ECHO.
ECHO Derleme islemi bitti.
ECHO Calistirilabilir dosya dist klasoru icinde bulunmaktadir.
ECHO.
ECHO.