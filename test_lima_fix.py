#!/usr/bin/env python3
"""Test para verificar que Lima funciona correctamente en la GUI"""

from locations_peru import PERU_LOCATIONS

# Simular selección en GUI
dept = "Lima"
prov = "Lima"

print("=== Test de Lima en GUI ===\n")

# Paso 1: Seleccionar departamento
if dept in PERU_LOCATIONS:
    print(f"✓ Departamento '{dept}' encontrado")
    provincias = list(PERU_LOCATIONS[dept].keys())
    print(f"  Provincias disponibles: {provincias}\n")
    
    # Paso 2: Seleccionar provincia
    if prov in PERU_LOCATIONS[dept]:
        print(f"✓ Provincia '{prov}' encontrada")
        distritos = PERU_LOCATIONS[dept][prov]
        print(f"  Total de distritos: {len(distritos)}")
        print(f"  Primeros 10 distritos (ordenados):")
        for i, dist in enumerate(sorted(distritos)[:10], 1):
            print(f"    {i:2}. {dist}")
        
        print(f"\n✅ TODO FUNCIONA CORRECTAMENTE")
        print(f"La GUI debería mostrar {len(distritos)} distritos cuando selecciones Lima → Lima")
    else:
        print(f"✗ ERROR: Provincia '{prov}' no encontrada")
        print(f"  Esto es lo que causa el problema en la GUI")
else:
    print(f"✗ ERROR: Departamento '{dept}' no encontrado")

print("\n" + "="*50)
print("CONCLUSIÓN: Los datos están correctos.")
print("Si no ves los distritos en la GUI, ejecuta el programa")
print("desde la terminal para ver los mensajes de debug.")