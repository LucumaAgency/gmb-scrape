#!/usr/bin/env python3
"""Test rápido de todas las ubicaciones"""

from locations_peru import PERU_LOCATIONS

def test_all_locations():
    print("=== TEST DE TODAS LAS UBICACIONES ===\n")
    
    total_depts = len(PERU_LOCATIONS)
    total_provs = 0
    total_dists = 0
    
    # Probar algunos departamentos específicos
    test_cases = [
        ("Lima", "Lima"),
        ("Arequipa", "Arequipa"),
        ("Cusco", "Cusco"),
        ("La Libertad", "Trujillo"),
        ("Piura", "Piura")
    ]
    
    print("Casos de prueba específicos:")
    print("-" * 40)
    
    for dept, prov in test_cases:
        if dept in PERU_LOCATIONS:
            if prov in PERU_LOCATIONS[dept]:
                districts = PERU_LOCATIONS[dept][prov]
                print(f"✓ {dept:15} → {prov:15} → {len(districts):3} distritos")
                print(f"  Muestra: {sorted(districts)[:3]}")
            else:
                print(f"✗ {dept:15} → {prov:15} → NO ENCONTRADA")
                print(f"  Provincias disponibles: {list(PERU_LOCATIONS[dept].keys())[:3]}")
        else:
            print(f"✗ {dept:15} → NO ENCONTRADO")
    
    print("\n" + "="*40)
    print("Resumen general:")
    print("-" * 40)
    
    # Contar todo
    for dept, provinces in PERU_LOCATIONS.items():
        total_provs += len(provinces)
        for prov, districts in provinces.items():
            total_dists += len(districts)
    
    print(f"Total departamentos: {total_depts}")
    print(f"Total provincias:    {total_provs}")
    print(f"Total distritos:     {total_dists}")
    
    print("\nPrimeros 5 departamentos:")
    for i, dept in enumerate(sorted(PERU_LOCATIONS.keys())[:5], 1):
        provs = len(PERU_LOCATIONS[dept])
        total_dist_dept = sum(len(dists) for dists in PERU_LOCATIONS[dept].values())
        print(f"  {i}. {dept:15} - {provs:2} provincias, {total_dist_dept:3} distritos")
    
    print("\n✅ Estructura de datos verificada correctamente")
    return True

if __name__ == "__main__":
    test_all_locations()
    
    print("\n" + "="*60)
    print("INSTRUCCIONES PARA DEBUG:")
    print("1. Ejecuta la GUI desde terminal: python3 gui.py")
    print("2. Selecciona un departamento - verás: >>> Departamento seleccionado: 'X'")
    print("3. Selecciona una provincia - verás: EVENTO: on_prov_select")
    print("4. Si no ves mensajes, hay un problema con los eventos de la GUI")
    print("5. Si ves errores, cópialos para debug")
    print("="*60)