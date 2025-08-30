#!/bin/bash

echo "====================================="
echo " GMB Scraper Peru - Actualizador"
echo "====================================="
echo ""

# Cambiar al directorio del script
cd "$(dirname "$0")"

echo "Verificando actualizaciones..."
python3 update.py

echo ""
echo "Proceso completado."
read -p "Presiona Enter para continuar..."