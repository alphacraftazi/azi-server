@echo off
title AZI SYSTEM CONTROLLER
color 0b
cls

echo ==================================================
echo   AZI - ALPHA CRAFT INTELLIGENCE SYSTEM STARTUP
echo ==================================================
echo.

echo [1/4] Sistem Kontrolleri Yapiliyor...
python -m pip install fastapi uvicorn sqlalchemy websockets google-generativeai python-dotenv duckduckgo-search requests pandas openpyxl selenium undetected-chromedriver > nul

echo [2/4] AZI Beyni (Server) Baslatiliyor...
start "AZI SERVER" cmd /k "python -m uvicorn azi_server.main:app --reload --host 0.0.0.0 --port 8001"

echo [3/4] Sunucu bekleniyor (3sn)...
timeout /t 3 >nul

echo.
echo Dashboard Tarayicida Aciliyor...
start http://localhost:8001/blackbox.html

echo.
echo ==================================================
echo   SISTEM TAMAMEN AKTIF
echo   - Sunucu: Calisiyor (Port 8000)
echo   - Client: Acildi
echo   - Bot: Hazir
echo ==================================================
echo.
echo Pencereyi kapatmayin, arka planda calisiyor...
pause
