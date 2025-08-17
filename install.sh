#!/bin/bash

echo "========================================"
echo "GMB Scraper Peru - Instalación Linux/Mac"
echo "========================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado."
    echo "Por favor instala Python 3 desde https://www.python.org/downloads/"
    exit 1
fi

echo "Python versión: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creando entorno virtual..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

echo "Instalando dependencias..."
echo ""

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "Intentando instalación alternativa..."
    pip install selenium
    pip install webdriver-manager
    pip install pandas || echo "pandas no disponible, usando CSV nativo"
    pip install python-dateutil
    pip install tqdm
    pip install beautifulsoup4
    pip install requests
    pip install undetected-chromedriver
    pip install openpyxl
    pip install lxml
fi

echo ""
echo "========================================"
echo "¡Instalación completada!"
echo ""
echo "Para usar el scraper:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo "========================================"