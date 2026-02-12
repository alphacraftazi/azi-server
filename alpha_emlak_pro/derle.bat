@echo off
title Alpha Craft Portfoy - EXE Derleme Araci
color 0A

echo ==================================================
echo       ALPHA CRAFT PORTFOY DERLEME MOTORU
echo ==================================================
echo.

echo [1/3] Gerekli kutuphaneler kontrol ediliyor...
:: Python modüllerini güncelle ve eksikleri tamamla
python -m pip install --upgrade pip
python -m pip install pyinstaller pywebview pandas openpyxl jinja2

echo.
echo [2/3] EXE derleme islemi baslatiliyor...
echo Lutfen bekleyin, bu islem bilgisayar hizina gore 1-3 dakika surebilir.
echo.

:: PATH sorununu asmak icin PyInstaller'i python modulu olarak cagiriyoruz (-m PyInstaller)
:: --noconfirm: Onay sormadan her seyi siler/yazar
:: --onefile: Tum dosyaları tek bir EXE içine paketler
:: --windowed: Program acildiginda arkada siyah konsol ekrani cikmaz
:: --add-data "index.html;.": index.html dosyasini EXE'nin icine gomulur
:: --name "Alpha Craft Portfoy": EXE'nin ismini belirler

python -m PyInstaller --noconfirm --onefile --windowed --add-data "index.html;." --name "Alpha Craft Portfoy" main.py

echo.
echo [3/3] Islem tamamlandi!
echo.
if exist dist\ (
    echo EXE dosyaniz 'dist' klasoru icinde basariyla olusturuldu.
    
    if exist license.key (
        copy license.key dist\license.key
        echo Lisans anahtari dist klasorune kopyalandi.
    )

    if exist *.xlsx (
        copy *.xlsx dist\
        echo Excel dosyalari dist klasorune kopyalandi.
    )

    if exist img\ (
        xcopy img dist\img /E /I /Y
        echo Gorsel dosyalar (img) kopyalandi.
    )

    if exist data\ (
        xcopy data dist\data /E /I /Y
        echo Veri klasoru (data) kopyalandi.
    )
) else (
    echo HATA: EXE olusturulamadi. Lutfen yukarıdaki hata mesajlarini kontrol edin.
)
echo.
echo NOT: Artik sadece 'dist' icindeki EXE'yi paylasmaniz yeterlidir. 
echo 'data' klasoru EXE ilk calistiginda EXE'nin yaninda otomatik olusacaktir.
echo.
pause