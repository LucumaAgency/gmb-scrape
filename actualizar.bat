@echo off
echo =====================================
echo  GMB Scraper Peru - Actualizador
echo =====================================
echo.

cd /d "%~dp0"

echo Verificando actualizaciones...
python update.py

echo.
echo Proceso completado.
pause