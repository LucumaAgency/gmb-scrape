#!/usr/bin/env python3
"""Prueba de volumen: 10 negocios en San Isidro.

Uso: python3 prueba_10_san_isidro.py [rubro] [cantidad]
Guarda salida_san_isidro.csv / .json y reporta cobertura y duplicados.
"""
import sys, json, logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

RUBRO = sys.argv[1] if len(sys.argv) > 1 else 'inmobiliaria'
CANTIDAD = int(sys.argv[2]) if len(sys.argv) > 2 else 10
SALIDA = 'salida_san_isidro'

from gmb_scraper_lite import GMBScraper

CAMPOS = ['name', 'rating', 'review_count', 'address', 'phone', 'website',
          'category', 'hours', 'email']

def vivo(v):
    return v not in (None, '', 'N/A', 0, [], 'No disponible')

def main():
    s = GMBScraper(headless=True)
    s.max_results_per_location = CANTIDAD
    try:
        s.init_driver()
        res = s.search_location(RUBRO, 'Lima', 'Lima', 'San Isidro', max_results=CANTIDAD)
        s.save_results(SALIDA, format='both')
    finally:
        try:
            s.close()
        except Exception:
            pass

    print(f"\n=== {len(res)} fichas extraidas ({RUBRO}, San Isidro) ===\n")
    for r in res:
        print(f"- {r.get('name','?')} | {r.get('rating')}* ({r.get('review_count')}) "
              f"| {r.get('phone','N/A')} | {r.get('email','N/A')}")

    claves = [(r.get('name'), r.get('address')) for r in res]
    unicos = len(set(claves))
    print(f"\nUnicos: {unicos}/{len(res)}  (duplicados: {len(res)-unicos})")

    print("\n=== COBERTURA POR CAMPO ===")
    for c in CAMPOS:
        n = sum(1 for r in res if vivo(r.get(c)))
        pct = (100*n//len(res)) if res else 0
        print(f"{c:15} {n}/{len(res)}  {pct}%")

    print(f"\nGuardado en {SALIDA}.csv / {SALIDA}.json")
    return 0 if res else 1

if __name__ == '__main__':
    sys.exit(main())
