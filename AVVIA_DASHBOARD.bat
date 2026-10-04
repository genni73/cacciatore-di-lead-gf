@echo off
title GF Lead Hunter
cd /d "%~dp0"

echo ========================================
echo   GF LEAD HUNTER - Avvio dashboard...
echo   Locale: http://localhost:5000
echo ========================================
echo.
echo (Lascia questa finestra aperta: chiudendola si spegne la dashboard)
echo.

python main.py dashboard

echo.
echo Dashboard terminata. Premi un tasto per chiudere.
pause > nul
