@echo off
echo ========================================
echo GMB Scraper Peru - Instalacion Windows
echo ========================================
echo.

REM Check Python version
python --version 2>NUL
if errorlevel 1 (
    echo ERROR: Python no esta instalado.
    echo Por favor instala Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Instalando dependencias...
echo.

REM Try regular requirements first
pip install -r requirements.txt 2>NUL

if errorlevel 1 (
    echo.
    echo Usando requirements alternativos para Windows...
    pip install -r requirements_windows.txt
    
    if errorlevel 1 (
        echo.
        echo Instalando dependencias una por una...
        pip install selenium
        pip install webdriver-manager
        pip install python-dateutil
        pip install tqdm
        pip install beautifulsoup4
        pip install requests
        pip install undetected-chromedriver
        pip install openpyxl
        pip install lxml
    )
)

echo.
echo ========================================
echo Instalacion completada!
echo.
echo Para usar el scraper ejecuta:
echo   python main.py
echo ========================================
pause