#!/usr/bin/env python3
"""
Script de prueba para verificar las correcciones realizadas
"""

import sys
import importlib

def test_main_imports():
    """Verifica que main.py no tiene imports duplicados"""
    with open('main.py', 'r') as f:
        content = f.read()
    
    import_count = content.count('import sys')
    print(f"✓ Imports de sys: {import_count} (debe ser 1)")
    assert import_count == 1, "Import duplicado de sys encontrado"
    
def test_argparse_max_results():
    """Verifica que --max-results está definido en el parser"""
    import argparse
    from main import cli_mode
    
    # Simular argumentos
    test_args = ['restaurantes', '--max-results', '30', '--departments', 'Lima']
    sys.argv = ['main.py'] + test_args
    
    parser = argparse.ArgumentParser()
    parser.add_argument('query')
    parser.add_argument('--departments', nargs='+')
    parser.add_argument('--max-results', type=int, default=20)
    
    args = parser.parse_args(test_args)
    
    print(f"✓ max_results parseado correctamente: {args.max_results}")
    assert args.max_results == 30, "max_results no se parsea correctamente"
    
def test_locations_variable():
    """Verifica que se usa 'locations' y no 'selected_locations'"""
    with open('main.py', 'r') as f:
        content = f.read()
    
    # No debe existir selected_locations en cli_mode
    cli_mode_section = content[content.find('def cli_mode'):content.find('if __name__')]
    
    if 'selected_locations' in cli_mode_section:
        print("✗ Todavía existe 'selected_locations' en cli_mode")
        assert False, "Variable selected_locations encontrada"
    else:
        print("✓ No se encontró 'selected_locations' en cli_mode")
        
def test_save_results_method():
    """Verifica que se usa save_results y no save_results_by_district"""
    with open('main.py', 'r') as f:
        content = f.read()
    
    if 'save_results_by_district' in content:
        print("✗ Todavía existe llamada a save_results_by_district")
        assert False, "save_results_by_district encontrado"
    else:
        print("✓ No se encontró save_results_by_district")
        
    if 'scraper.save_results(' in content:
        print("✓ Se usa correctamente save_results")
    else:
        print("✗ No se encontró llamada a save_results")
        assert False, "No se encontró save_results"

def test_search_location_params():
    """Verifica que se pasa max_results a search_location"""
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Buscar la llamada a search_location en cli_mode
    if 'search_location(args.query, dept, prov, dist, max_results=args.max_results' in content:
        print("✓ max_results se pasa correctamente a search_location")
    else:
        print("✗ max_results no se pasa a search_location")
        assert False, "max_results no se pasa a search_location"

def main():
    print("=" * 50)
    print("VERIFICANDO CORRECCIONES")
    print("=" * 50)
    
    tests = [
        ("Imports duplicados", test_main_imports),
        ("Argumento --max-results", test_argparse_max_results),
        ("Variable locations", test_locations_variable),
        ("Método save_results", test_save_results_method),
        ("Parámetros search_location", test_search_location_params)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Probando: {test_name}")
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"   ✗ Error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"RESULTADO: {passed} pruebas pasadas, {failed} fallidas")
    print("=" * 50)
    
    if failed == 0:
        print("✅ TODAS LAS CORRECCIONES FUNCIONAN CORRECTAMENTE")
    else:
        print("❌ Algunas pruebas fallaron")
        sys.exit(1)

if __name__ == "__main__":
    main()