#!/usr/bin/env python3
"""Siembra vistos.jsonl con lo ya scrapeado en corridas anteriores.

Uso una sola vez, para que el historial arranque sabiendo todo lo que ya
tenemos. Despues correr_campana.py lo mantiene solo.

    python3 sembrar_vistos.py *.json
"""
import json
import sys

from progreso import HistorialVistos


def main():
    rutas = sys.argv[1:]
    if not rutas:
        print(__doc__)
        return 1

    historial = HistorialVistos()
    print(f"Historial actual: {historial.negocios} negocios")

    for ruta in rutas:
        try:
            with open(ruta, encoding='utf-8') as f:
                datos = json.load(f)
        except Exception as e:
            print(f"  {ruta}: ilegible ({e})")
            continue

        if not isinstance(datos, list) or not datos or not isinstance(datos[0], dict):
            continue
        if 'name' not in datos[0]:
            continue  # no es una salida del scraper

        nuevos = historial.agregar(datos)
        print(f"  {ruta}: {len(datos)} fichas -> {nuevos} nuevas al historial")

    print(f"Historial final: {historial.negocios} negocios unicos")
    return 0


if __name__ == '__main__':
    sys.exit(main())
