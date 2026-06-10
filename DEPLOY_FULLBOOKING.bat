@echo off
chcp 65001 >nul
echo.
echo ================================================
echo   FULL BOOKING — Deploy Preview su Netlify
echo   GF Technological System / Gennaro Fusco
echo ================================================
echo.

cd /d "%~dp0"

REM Controlla che netlify CLI sia installato
where netlify >nul 2>&1
if errorlevel 1 (
    echo [!] Netlify CLI non trovato. Installo ora...
    npm install -g netlify-cli
    echo.
)

echo [1/3] Numero preview da caricare:
dir /b preview_fullbooking\*.html 2>nul | find /c ".html"
echo.

echo [2/3] Deploy su Netlify in corso...
echo       (Prima volta: ti chiede di fare login e scegliere il sito)
echo       Quando chiede il nome del sito, scrivi: fullbooking
echo.

netlify deploy --prod --dir=preview_fullbooking --site=fullbooking

echo.
echo [3/3] FATTO!
echo.
echo Il tuo URL permanente e':
echo   https://fullbooking.netlify.app
echo.
echo Copia questo URL in config.py alla riga FULLBOOKING_BASE_URL
echo.
echo Ora puoi inviare i messaggi con:
echo   python main.py fullbooking-wa
echo.
pause
