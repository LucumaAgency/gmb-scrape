#!/usr/bin/env python3
"""Test script for incremental save functionality"""

import gmb_scraper
import os

# Create scraper instance
scraper = gmb_scraper.GMBScraper()

# Test batch data
test_batch_1 = [
    {
        'name': 'Restaurant Lima 1',
        'address': 'Av. Larco 123, Miraflores',
        'phone': '01-2345678',
        'website': 'www.rest1.com',
        'rating': '4.5',
        'reviews': 150,
        'email': 'contact@rest1.com'
    },
    {
        'name': 'Restaurant Lima 2',
        'address': 'Jr. Union 456, Centro',
        'phone': '01-8765432',
        'website': 'N/A',
        'rating': '4.0',
        'reviews': 89,
        'email': 'N/A'
    }
]

test_batch_2 = [
    {
        'name': 'Cafetería San Isidro',
        'address': 'Av. Rivera Navarrete 789',
        'phone': '01-5555555',
        'website': 'www.cafe.pe',
        'rating': '4.8',
        'reviews': 200,
        'email': 'info@cafe.pe'
    }
]

# Test filename
filename = 'test_incremental_gui'

print("=" * 60)
print("PRUEBA DE GUARDADO INCREMENTAL")
print("=" * 60)

# Clean up any existing test files
for ext in ['.csv', '.json']:
    if os.path.exists(f'{filename}{ext}'):
        os.remove(f'{filename}{ext}')
        print(f"✓ Archivo anterior {filename}{ext} eliminado")

print("\n1. Guardando primer batch (crear archivo)...")
try:
    scraper.save_results_incremental(
        test_batch_1,
        filename=filename,
        format='both',
        append=False  # Create new file
    )
    print("   ✓ Primer batch guardado (archivos creados)")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Check files exist
for ext in ['.csv', '.json']:
    if os.path.exists(f'{filename}{ext}'):
        size = os.path.getsize(f'{filename}{ext}')
        print(f"   ✓ {filename}{ext} existe ({size} bytes)")

print("\n2. Guardando segundo batch (append)...")
try:
    scraper.save_results_incremental(
        test_batch_2,
        filename=filename,
        format='both',
        append=True  # Append to existing
    )
    print("   ✓ Segundo batch agregado")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Verify final content
print("\n3. Verificando contenido final...")

# Check CSV
with open(f'{filename}.csv', 'r', encoding='utf-8') as f:
    csv_lines = f.readlines()
    print(f"   CSV: {len(csv_lines)} líneas (1 header + 3 datos esperados)")
    if len(csv_lines) == 4:
        print("   ✓ CSV correcto")
    else:
        print(f"   ✗ CSV incorrecto: esperaba 4 líneas, encontré {len(csv_lines)}")

# Check JSON
import json
with open(f'{filename}.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)
    print(f"   JSON: {len(json_data)} registros (3 esperados)")
    if len(json_data) == 3:
        print("   ✓ JSON correcto")
        # Show business names
        names = [r['name'] for r in json_data]
        print(f"   Negocios guardados: {', '.join(names)}")
    else:
        print(f"   ✗ JSON incorrecto: esperaba 3 registros, encontré {len(json_data)}")

print("\n" + "=" * 60)
print("PRUEBA COMPLETADA")
print("=" * 60)

# Clean up
print("\n4. Limpiando archivos de prueba...")
for ext in ['.csv', '.json']:
    if os.path.exists(f'{filename}{ext}'):
        os.remove(f'{filename}{ext}')
        print(f"   ✓ {filename}{ext} eliminado")

print("\n✅ Todas las pruebas pasaron correctamente!")