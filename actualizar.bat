@echo off
echo =====================================
echo  GMB Scraper Peru - Actualizador
echo =====================================
echo.

cd /d "%~dp0"

echo Ejecutando actualizacion...
echo.

REM Intentar con python3 primero, luego python
python3 simple_update.py 2>nul || python simple_update.py 2>nul || (
    echo No se encontro Python. Ejecutando git pull directamente...
    git pull origin main
    echo.
    pause
)