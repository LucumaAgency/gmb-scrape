@echo off
title GMB Scraper Peru - Interfaz Grafica
color 0A

echo ============================================
echo      GMB Scraper Peru v1.0
echo      Extractor de Google My Business
echo ============================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo.
    echo Por favor:
    echo 1. Instale Python desde https://www.python.org/downloads/
    echo 2. Durante la instalacion, marque "Add Python to PATH"
    echo 3. Reinicie esta ventana y ejecute nuevamente
    echo.
    pause
    exit /b 1
)

echo [OK] Python detectado
echo.

REM Verificar si tkinter está instalado
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] tkinter no esta instalado
    echo Instalando tkinter...
    pip install tk
)

REM Verificar dependencias básicas
echo Verificando dependencias...
python -c "import selenium" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias faltantes...
    pip install selenium webdriver-manager pandas beautifulsoup4 requests tqdm openpyxl lxml
)

echo.
echo Iniciando GMB Scraper Peru...
echo ============================================
echo.

REM Ejecutar la GUI
python gui.py

if errorlevel 1 (
    echo.
    echo ============================================
    echo [ERROR] El programa no se pudo ejecutar
    echo.
    echo Posibles soluciones:
    echo 1. Ejecute: python installer_windows.py
    echo 2. O instale manualmente: pip install -r requirements.txt
    echo ============================================
    pause
)