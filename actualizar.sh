#!/bin/bash

echo "====================================="
echo " GMB Scraper Peru - Actualizador"
echo "====================================="
echo ""

# Cambiar al directorio del script
cd "$(dirname "$0")"

echo "Ejecutando actualización..."
echo ""

# Intentar con python3, si falla usar python
if command -v python3 &> /dev/null; then
    python3 simple_update.py
elif command -v python &> /dev/null; then
    python simple_update.py
else
    echo "Python no encontrado. Ejecutando git pull directamente..."
    git pull origin main
    echo ""
    read -p "Presiona Enter para continuar..."
fi