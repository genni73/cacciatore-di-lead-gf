@echo off
title GF Lead Hunter - Avvio Automatico
cd /d "C:\Users\genna\Desktop\gf-lead-hunter"

echo.
echo ========================================
echo   GF LEAD HUNTER - Avvio in corso...
echo ========================================
echo.

REM Avvia Flask in background
echo [1/2] Avvio server dashboard...
start /B python main.py dashboard > nul 2>&1

REM Aspetta 3 secondi
timeout /t 3 /nobreak > nul

REM Avvia ngrok in background
echo [2/2] Avvio tunnel ngrok...
start /B ngrok http 5000 > nul 2>&1

REM Aspetta che ngrok si avvii
timeout /t 4 /nobreak > nul

REM Prendi il link ngrok dall'API locale
echo.
echo Recupero link pubblico...
for /f "tokens=*" %%a in ('powershell -command "(Invoke-WebRequest -Uri http://localhost:4040/api/tunnels -UseBasicParsing | ConvertFrom-Json).tunnels[0].public_url"') do set NGROK_URL=%%a

echo.
echo ========================================
echo   DASHBOARD PRONTA!
echo   Link locale:   http://localhost:5000
echo   Link pubblico: %NGROK_URL%
echo ========================================
echo.

REM Apri il browser
start "" "%NGROK_URL%"

echo Premi un tasto per chiudere questa finestra (dashboard continua in background)
pause > nul
