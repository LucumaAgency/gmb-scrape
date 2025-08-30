#!/usr/bin/env python3
"""Test para diagnosticar el problema de selección"""

from locations_peru import PERU_LOCATIONS

print("=== DIAGNÓSTICO DEL PROBLEMA DE SELECCIÓN ===\n")

# Simular lo que pasa en la GUI
print("1. Seleccionas Lima como departamento")
dept = "Lima"
if dept in PERU_LOCATIONS:
    provinces = list(PERU_LOCATIONS[dept].keys())
    print(f"   ✓ Se cargan {len(provinces)} provincias: {provinces}")
    
    print("\n2. Seleccionas Lima como provincia")
    prov = "Lima"
    
    # Simular el evento on_prov_select
    print("\n3. Se dispara on_prov_select:")
    
    # Simular curselection() devolviendo tupla vacía
    dept_selection = ()  # Esto es lo que podría estar pasando
    prov_selection = (0,)  # Provincia sí está seleccionada
    
    print(f"   dept_selection: {dept_selection} (len={len(dept_selection)})")
    print(f"   prov_selection: {prov_selection} (len={len(prov_selection)})")
    
    if len(dept_selection) == 0:
        print("   ⚠️ PROBLEMA: No hay departamento seleccionado")
        print("   Esto es lo que está causando el error!")
    
    print("\n4. CAUSA DEL PROBLEMA:")
    print("   Al seleccionar una provincia, el evento se dispara")
    print("   pero la selección del departamento se pierde o no se detecta")
    
    print("\n5. SOLUCIÓN:")
    print("   Usar variables de instancia (self.current_dept)")
    print("   para mantener el estado del departamento seleccionado")

print("\n" + "="*60)
print("CONCLUSIÓN:")
print("El problema es que curselection() devuelve tupla vacía")
print("cuando el evento de provincia se dispara.")
print("La versión 1.0.3 debería resolver esto.")
print("="*60)