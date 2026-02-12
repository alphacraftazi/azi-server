@echo off
echo TUM PYTHON ISLEMLERI KAPATILIYOR...
taskkill /F /IM python.exe
taskkill /F /IM pythonw.exe
taskkill /F /IM uvicorn.exe
echo.
echo Temizlik tamamlandi.
echo.
echo AZI YENIDEN BASLATILIYOR...
echo.
start cmd /k "python -m uvicorn azi_server.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3
start http://localhost:8000
echo.
echo Islem tamam. Lutfen yeni acilan sayfayi kullanin.
pause
