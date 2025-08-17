#!/usr/bin/env python3
import argparse
import json
from gmb_scraper import GMBScraper
from locations_peru import PERU_LOCATIONS
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_banner():
    print("""
    ╔════════════════════════════════════════╗
    ║     Google My Business Scraper Peru    ║
    ║         Filtrado por Ubicación         ║
    ║           + Extracción de Emails       ║
    ╚════════════════════════════════════════╝
    """)

def get_user_locations():
    print("\n📍 SELECCIÓN DE UBICACIONES")
    print("-" * 40)
    
    departments = list(PERU_LOCATIONS.keys())
    print("\nDepartamentos disponibles:")
    for i, dept in enumerate(departments, 1):
        print(f"{i:2}. {dept}")
    
    selected_locations = []
    
    while True:
        dept_input = input("\n🏛️ Seleccione departamento (número o 'todos' para todos): ").strip()
        
        if dept_input.lower() == 'todos':
            for dept in departments:
                for prov in PERU_LOCATIONS[dept]:
                    for dist in PERU_LOCATIONS[dept][prov]:
                        selected_locations.append((dept, prov, dist))
            break
        
        try:
            dept_idx = int(dept_input) - 1
            if 0 <= dept_idx < len(departments):
                selected_dept = departments[dept_idx]
                provinces = list(PERU_LOCATIONS[selected_dept].keys())
                
                print(f"\nProvincias en {selected_dept}:")
                for i, prov in enumerate(provinces, 1):
                    print(f"{i:2}. {prov}")
                
                prov_input = input("\n🏙️ Seleccione provincia (número o 'todos'): ").strip()
                
                if prov_input.lower() == 'todos':
                    for prov in provinces:
                        for dist in PERU_LOCATIONS[selected_dept][prov]:
                            selected_locations.append((selected_dept, prov, dist))
                else:
                    prov_idx = int(prov_input) - 1
                    if 0 <= prov_idx < len(provinces):
                        selected_prov = provinces[prov_idx]
                        districts = PERU_LOCATIONS[selected_dept][selected_prov]
                        
                        print(f"\nDistritos en {selected_prov}:")
                        for i, dist in enumerate(districts, 1):
                            print(f"{i:2}. {dist}")
                        
                        dist_input = input("\n🏘️ Seleccione distrito(s) (números separados por coma o 'todos'): ").strip()
                        
                        if dist_input.lower() == 'todos':
                            for dist in districts:
                                selected_locations.append((selected_dept, selected_prov, dist))
                        else:
                            dist_indices = [int(x.strip()) - 1 for x in dist_input.split(',')]
                            for idx in dist_indices:
                                if 0 <= idx < len(districts):
                                    selected_locations.append((selected_dept, selected_prov, districts[idx]))
                
                add_more = input("\n¿Agregar más ubicaciones? (s/n): ").strip().lower()
                if add_more != 's':
                    break
                    
        except (ValueError, IndexError):
            print("❌ Selección inválida. Intente nuevamente.")
    
    return selected_locations

def get_filters():
    print("\n⚙️ CONFIGURACIÓN DE FILTROS")
    print("-" * 40)
    
    filters = {}
    
    try:
        min_rating = input("⭐ Rating mínimo (0-5, Enter para 0): ").strip()
        filters['min_rating'] = float(min_rating) if min_rating else 0
        
        min_reviews = input("💬 Cantidad mínima de reviews (Enter para 0): ").strip()
        filters['min_reviews'] = int(min_reviews) if min_reviews else 0
        
        min_age = input("📅 Antigüedad mínima en días (Enter para 0): ").strip()
        filters['min_age_days'] = int(min_age) if min_age else 0
        
        max_age = input("📅 Antigüedad máxima en días (Enter para sin límite): ").strip()
        filters['max_age_days'] = int(max_age) if max_age else 36500
        
    except ValueError:
        print("❌ Valor inválido. Usando valores por defecto.")
        filters = {'min_rating': 0, 'min_reviews': 0, 'min_age_days': 0, 'max_age_days': 36500}
    
    return filters

def interactive_mode():
    print_banner()
    
    query = input("🔍 Ingrese el término de búsqueda (ej: 'restaurantes', 'hoteles'): ").strip()
    if not query:
        print("❌ Debe ingresar un término de búsqueda")
        return
    
    locations = get_user_locations()
    if not locations:
        print("❌ No se seleccionaron ubicaciones")
        return
    
    filters = get_filters()
    
    output_format = input("\n💾 Formato de salida (csv/json/both): ").strip().lower()
    if output_format not in ['csv', 'json', 'both']:
        output_format = 'both'
    
    headless = input("🖥️ Ejecutar en modo headless? (s/n): ").strip().lower() == 's'
    
    print(f"\n📊 Resumen de búsqueda:")
    print(f"   - Término: {query}")
    print(f"   - Ubicaciones: {len(locations)} seleccionadas")
    print(f"   - Filtros: {filters}")
    print(f"   - Formato: {output_format}")
    
    confirm = input("\n¿Iniciar búsqueda? (s/n): ").strip().lower()
    if confirm != 's':
        print("Búsqueda cancelada")
        return
    
    scraper = GMBScraper(headless=headless)
    try:
        scraper.init_driver()
        
        print(f"\n🚀 Iniciando búsqueda de '{query}'...")
        total_found = 0
        total_with_emails = 0
        
        for dept, prov, dist in locations:
            results = scraper.search_location(query, dept, prov, dist, **filters)
            total_found += len(results)
            emails_found = sum(1 for r in results if r.get('email', 'N/A') != 'N/A')
            total_with_emails += emails_found
            print(f"   ✓ {dist}, {prov}, {dept}: {len(results)} resultados ({emails_found} con email)")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gmb_{query.replace(' ', '_')}_{timestamp}"
        scraper.save_results(filename, output_format)
        
        print(f"\n✅ Búsqueda completada:")
        print(f"   - Total de negocios encontrados: {total_found}")
        print(f"   - Negocios con email: {total_with_emails}")
        print(f"   - Resultados guardados en: {filename}.{output_format if output_format != 'both' else 'csv y .json'}")
        
    except Exception as e:
        logger.error(f"Error durante la búsqueda: {e}")
    finally:
        scraper.close()

def cli_mode():
    parser = argparse.ArgumentParser(description='Google My Business Scraper para Perú')
    parser.add_argument('query', help='Término de búsqueda (ej: restaurantes, hoteles)')
    parser.add_argument('--departments', nargs='+', help='Departamentos a buscar')
    parser.add_argument('--provinces', nargs='+', help='Provincias a buscar')
    parser.add_argument('--districts', nargs='+', help='Distritos a buscar')
    parser.add_argument('--min-rating', type=float, default=0, help='Rating mínimo (0-5)')
    parser.add_argument('--min-reviews', type=int, default=0, help='Cantidad mínima de reviews')
    parser.add_argument('--min-age', type=int, default=0, help='Antigüedad mínima en días')
    parser.add_argument('--max-age', type=int, default=36500, help='Antigüedad máxima en días')
    parser.add_argument('--output', default='gmb_results', help='Nombre del archivo de salida')
    parser.add_argument('--format', choices=['csv', 'json', 'both'], default='both', help='Formato de salida')
    parser.add_argument('--headless', action='store_true', help='Ejecutar en modo headless')
    parser.add_argument('--config', help='Archivo de configuración JSON')
    
    args = parser.parse_args()
    
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
            locations = config.get('locations', [])
            filters = config.get('filters', {})
    else:
        locations = []
        if args.departments:
            for dept in args.departments:
                if dept in PERU_LOCATIONS:
                    for prov in PERU_LOCATIONS[dept]:
                        for dist in PERU_LOCATIONS[dept][prov]:
                            locations.append((dept, prov, dist))
        
        filters = {
            'min_rating': args.min_rating,
            'min_reviews': args.min_reviews,
            'min_age_days': args.min_age,
            'max_age_days': args.max_age
        }
    
    if not locations:
        print("❌ No se especificaron ubicaciones válidas")
        return
    
    scraper = GMBScraper(headless=args.headless)
    try:
        scraper.init_driver()
        
        print(f"🚀 Buscando '{args.query}'...")
        total_found = 0
        total_with_emails = 0
        
        for dept, prov, dist in locations:
            results = scraper.search_location(args.query, dept, prov, dist, **filters)
            total_found += len(results)
            emails_found = sum(1 for r in results if r.get('email', 'N/A') != 'N/A')
            total_with_emails += emails_found
            print(f"   ✓ {dist}, {prov}: {len(results)} resultados ({emails_found} con email)")
        
        scraper.save_results(args.output, args.format)
        print(f"\n✅ Búsqueda completada:")
        print(f"   - Total de negocios: {total_found}")
        print(f"   - Con email: {total_with_emails}")
        print(f"   - Guardado en: {args.output}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] != '--interactive':
        cli_mode()
    else:
        interactive_mode()