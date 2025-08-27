@echo off
echo ========================================
echo  Creando accesos directos GMB Scraper
echo ========================================
echo.

REM Obtener la ruta actual
set CURRENT_DIR=%~dp0

REM Crear acceso directo en el escritorio
echo Creando acceso directo en el escritorio...
(
echo @echo off
echo cd /d "%CURRENT_DIR%"
echo python gui.py
echo pause
) > "%USERPROFILE%\Desktop\GMB Scraper Peru.bat"

if exist "%USERPROFILE%\Desktop\GMB Scraper Peru.bat" (
    echo [OK] Acceso directo creado en el escritorio
) else (
    echo [ERROR] No se pudo crear en el escritorio
)

REM Crear acceso directo alternativo para ejecutar con Python
(
echo @echo off
echo cd /d "%CURRENT_DIR%"
echo echo ========================================
echo echo     GMB Scraper Peru - Iniciando
echo echo ========================================
echo echo.
echo echo Verificando Python...
echo python --version
echo echo.
echo echo Iniciando interfaz grafica...
echo python gui.py
echo if errorlevel 1 (
echo     echo.
echo     echo ERROR: No se pudo iniciar el programa
echo     echo Posibles soluciones:
echo     echo 1. Instale Python desde python.org
echo     echo 2. Ejecute: pip install -r requirements.txt
echo     echo 3. Ejecute: python installer_windows.py
echo     pause
echo )
) > "%USERPROFILE%\Desktop\GMB Scraper Peru GUI.bat"

REM Crear acceso directo para línea de comandos
(
echo @echo off
echo cd /d "%CURRENT_DIR%"
echo cmd /k "python main.py --help"
) > "%USERPROFILE%\Desktop\GMB Scraper Peru CLI.bat"

echo.
echo ========================================
echo Accesos directos creados:
echo ========================================
echo 1. GMB Scraper Peru.bat - Ejecuta la interfaz grafica
echo 2. GMB Scraper Peru GUI.bat - Version con diagnostico
echo 3. GMB Scraper Peru CLI.bat - Linea de comandos
echo.
echo Los encontraras en tu escritorio
echo.
echo Tambien puedes ejecutar directamente:
echo   - Interfaz grafica: python gui.py
echo   - Linea de comandos: python main.py --help
echo.
pause