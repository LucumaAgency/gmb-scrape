#!/usr/bin/env python3
"""Prueba de humo: verifica si el scraper todavia extrae datos de Google Maps.

Corre una sola busqueda en un distrito y reporta que campos siguen vivos.
Uso: python3 smoke_test.py [rubro] [distrito]
"""
import sys, json, logging, traceback

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

QUERY = sys.argv[1] if len(sys.argv) > 1 else 'restaurantes'
DISTRITO = sys.argv[2] if len(sys.argv) > 2 else 'Miraflores'

from gmb_scraper_lite import GMBScraper

CAMPOS = ['name', 'rating', 'review_count', 'address', 'phone', 'website',
          'category', 'hours', 'emails']

def main():
    s = GMBScraper(headless=True)
    s.max_results_per_location = 3
    try:
        s.init_driver()
        print(f"\n>>> Buscando '{QUERY}' en {DISTRITO}, Lima, Lima\n")
        res = s.search_location(QUERY, 'Lima', 'Lima', DISTRITO, max_results=3)
        print(f"\n=== RESULTADOS: {len(res)} ===\n")
        print(json.dumps(res, ensure_ascii=False, indent=2)[:4000])

        print("\n=== SALUD DE CAMPOS ===")
        if not res:
            print("SIN RESULTADOS -> los selectores o la busqueda estan rotos")
            return 1
        for c in CAMPOS:
            vivos = sum(1 for r in res
                        if r.get(c) not in (None, '', 'N/A', 0, [], 'No disponible'))
            estado = 'OK ' if vivos else 'ROTO'
            print(f"{estado} {c:15} {vivos}/{len(res)}")
        return 0
    except Exception:
        traceback.print_exc()
        return 2
    finally:
        try:
            s.close()
        except Exception:
            pass

if __name__ == '__main__':
    sys.exit(main())
