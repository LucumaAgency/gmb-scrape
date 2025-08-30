#!/usr/bin/env python3
"""Script para probar que los distritos de Lima se muestren correctamente"""

from locations_peru import PERU_LOCATIONS

def test_lima_data():
    print("=== Verificando datos de Lima ===\n")
    
    # Verificar que Lima existe
    if "Lima" in PERU_LOCATIONS:
        print("✓ Departamento Lima encontrado")
        
        # Verificar provincias de Lima
        lima_provinces = PERU_LOCATIONS["Lima"]
        print(f"✓ Total de provincias en Lima: {len(lima_provinces)}")
        print(f"  Provincias: {', '.join(lima_provinces.keys())}\n")
        
        # Verificar distritos de Lima provincia
        if "Lima" in lima_provinces:
            lima_districts = lima_provinces["Lima"]
            print(f"✓ Provincia Lima encontrada")
            print(f"✓ Total de distritos en Lima provincia: {len(lima_districts)}")
            print(f"\nPrimeros 15 distritos:")
            for i, district in enumerate(lima_districts[:15], 1):
                print(f"  {i:2}. {district}")
            
            # Verificar distritos importantes
            important_districts = ["Miraflores", "San Isidro", "Barranco", "San Borja", "La Molina"]
            print(f"\nDistritos importantes:")
            for dist in important_districts:
                if dist in lima_districts:
                    print(f"  ✓ {dist} encontrado")
                else:
                    print(f"  ✗ {dist} NO encontrado")
        else:
            print("✗ Provincia Lima NO encontrada en departamento Lima")
    else:
        print("✗ Departamento Lima NO encontrado")

if __name__ == "__main__":
    test_lima_data()
    
    print("\n=== Simulación de selección en GUI ===")
    print("\n1. Usuario selecciona departamento: Lima")
    print("   → Se cargan provincias:", list(PERU_LOCATIONS["Lima"].keys())[:5], "...")
    
    print("\n2. Usuario selecciona provincia: Lima")
    lima_dists = PERU_LOCATIONS["Lima"]["Lima"]
    print(f"   → Se cargan {len(lima_dists)} distritos")
    print(f"   → Muestra: {lima_dists[:5]} ...")
    
    print("\n✓ El flujo de datos es correcto. Si no se ven los distritos en la GUI,")
    print("  el problema está en el código de la interfaz, no en los datos.")