@echo off
title AZI LOCAL SERVER
color 0a
cls
echo ===================================================
echo  AZI LOCAL SERVER (SYSTEM BUILD MODE)
echo ===================================================
echo.
echo  Local ortam baslatiliyor...
echo  Bu modda 'Sistem Insa' (EXE Derleme) calisabilir.
echo.

:: Python Environment Setup (Adjust path if needed)
set PYTHONPATH=%cd%

:: Activate Virtual Env if exists (Optional)
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

:: Run Server
uvicorn azi_server.main:app --host 127.0.0.1 --port 8001 --reload

pause
