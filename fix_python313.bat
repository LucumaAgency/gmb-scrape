@echo off
echo ========================================
echo Fix para Python 3.13 - GMB Scraper
echo ========================================
echo.

echo Instalando setuptools para compatibilidad con distutils...
pip install setuptools

echo.
echo Desinstalando undetected-chromedriver...
pip uninstall undetected-chromedriver -y

echo.
echo Instalando dependencias basicas...
pip install selenium
pip install webdriver-manager
pip install beautifulsoup4
pip install requests
pip install python-dateutil
pip install tqdm
pip install openpyxl
pip install lxml

echo.
echo ========================================
echo Fix aplicado!
echo.
echo El scraper ahora usara la version lite
echo que es compatible con Python 3.13
echo.
echo Ejecuta: python main.py
echo ========================================
pause