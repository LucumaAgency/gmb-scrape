#!/usr/bin/env python3
"""Corrida larga y reanudable: varios rubros x varios distritos.

Aborta ante el primer bloqueo de Google, guarda cada lote apenas lo obtiene y
recuerda que combinaciones ya hizo, asi que se puede relanzar sin repetir nada.

Ejemplos:
    python3 correr_campana.py --rubros inmobiliaria,estudio contable \\
        --distritos "San Isidro,Miraflores,Surco" --por-busqueda 10 --tope 100

    python3 correr_campana.py --estado          # ver progreso acumulado
"""
import argparse
import json
import os
import sys
import logging

from gmb_scraper_lite import GMBScraper, BloqueoDetectado
from progreso import RegistroProgreso, HistorialVistos

logger = logging.getLogger('campana')


def parse_args():
    p = argparse.ArgumentParser(description='Corrida GMB reanudable con corte ante bloqueo')
    p.add_argument('--rubros', default='inmobiliaria',
                   help='lista separada por comas')
    p.add_argument('--distritos', default='San Isidro',
                   help='lista separada por comas (dentro de Lima/Lima salvo --departamento)')
    p.add_argument('--departamento', default='Lima')
    p.add_argument('--provincia', default='Lima')
    p.add_argument('--por-busqueda', type=int, default=10,
                   help='fichas maximas por combinacion rubro-distrito')
    p.add_argument('--tope', type=int, default=300,
                   help='tope duro de fichas para toda la sesion (recomendado 300-500/dia por IP)')
    p.add_argument('--pausa', default='20,40',
                   help='rango en segundos de pausa entre busquedas')
    p.add_argument('--salida', default='campana_gmb')
    p.add_argument('--progreso', default='progreso.jsonl')
    p.add_argument('--headless', action='store_true', default=True)
    p.add_argument('--estado', action='store_true', help='solo mostrar el progreso y salir')
    p.add_argument('--vistos', default='vistos.jsonl',
                   help='historial de negocios ya extraidos en TODAS las corridas; '
                        'se carga y actualiza solo, para no repetir de un dia a otro')
    p.add_argument('--sin-historial', action='store_true',
                   help='ignorar el historial y permitir re-scrapear lo ya visto')
    p.add_argument('--excluir', default='',
                   help='JSON(s) de corridas previas, separados por coma: sus negocios se saltan '
                        'sin volver a abrirlos (para pedir "otros N" del mismo rubro y distrito)')
    return p.parse_args()


def cargar_excluidos(rutas):
    """Devuelve las claves (place_id y nombre|direccion) de corridas previas."""
    claves = set()
    for ruta in [r.strip() for r in rutas.split(',') if r.strip()]:
        if not os.path.exists(ruta):
            print(f"Aviso: no existe {ruta}, se ignora")
            continue
        try:
            with open(ruta, encoding='utf-8') as f:
                datos = json.load(f)
        except Exception as e:
            print(f"Aviso: no se pudo leer {ruta} ({e})")
            continue
        for reg in datos:
            if reg.get('place_id'):
                claves.add(reg['place_id'])
            claves.add(f"{reg.get('name','')}|{reg.get('address','')}".lower())
        print(f"{ruta}: {len(datos)} negocios previos que no se volveran a abrir")
    return claves


def main():
    args = parse_args()
    registro = RegistroProgreso(args.progreso)

    if args.estado:
        r = registro.resumen()
        print(f"Combinaciones hechas: {r['combinaciones']}")
        print(f"Fichas acumuladas:    {r['fichas']}")
        print(f"Sin resultados:       {r['sin_resultados']}")
        return 0

    rubros = [x.strip() for x in args.rubros.split(',') if x.strip()]
    distritos = [x.strip() for x in args.distritos.split(',') if x.strip()]
    pausa_min, pausa_max = (float(x) for x in args.pausa.split(','))

    combinaciones = [(r, d) for r in rubros for d in distritos]
    pendientes = [(r, d) for r, d in combinaciones
                  if not registro.ya_hecha(r, args.departamento, args.provincia, d)]

    print(f"\n{len(combinaciones)} combinaciones, {len(pendientes)} pendientes "
          f"({len(combinaciones) - len(pendientes)} ya hechas se saltan)")
    if not pendientes:
        print("Nada que hacer.")
        return 0

    print(f"Tope de sesion: {args.tope} fichas · {args.por_busqueda} por busqueda "
          f"· pausa {pausa_min}-{pausa_max}s\n")

    s = GMBScraper(headless=args.headless)
    s.max_results_per_location = args.por_busqueda
    s.max_fichas_sesion = args.tope
    s.pausa_entre_busquedas = (pausa_min, pausa_max)

    # Historial acumulado: la unica garantia de que una corrida de otro dia
    # no vuelva a extraer los mismos negocios.
    historial = HistorialVistos(args.vistos)
    if args.sin_historial:
        print("Historial DESACTIVADO: se puede re-scrapear lo ya visto")
        historial.claves = set()
    elif historial.negocios:
        print(f"Historial: {historial.negocios} negocios ya extraidos que no se volveran a abrir")

    s.vistos = set(historial.claves)
    if args.excluir:
        s.vistos |= cargar_excluidos(args.excluir)

    codigo = 0
    try:
        s.init_driver()

        for i, (rubro, distrito) in enumerate(pendientes, 1):
            if s.fichas_extraidas >= args.tope:
                print(f"\nTope de sesion alcanzado ({args.tope} fichas). "
                      f"Relanza manana para continuar.")
                break

            print(f"[{i}/{len(pendientes)}] {rubro} en {distrito} "
                  f"(acumulado: {s.fichas_extraidas}/{args.tope})")

            lote = s.search_location(rubro, args.departamento, args.provincia, distrito,
                                     max_results=args.por_busqueda)

            if lote:
                s.save_results_incremental(lote, args.salida, format='both', append=True)
                if not args.sin_historial:
                    historial.agregar(lote)
                    s.vistos = set(historial.claves)

            # Si el tope corto la busqueda a la mitad, queda 'parcial' para
            # reintentarla completa en la proxima corrida.
            cortada = (s.fichas_extraidas >= args.tope and len(lote) < args.por_busqueda)
            estado = 'parcial' if cortada else 'ok'
            registro.marcar(rubro, args.departamento, args.provincia, distrito, len(lote), estado)
            print(f"    -> {len(lote)} fichas{' (parcial, se reintentara)' if cortada else ''}")

    except BloqueoDetectado as e:
        # Lo importante: cortar y decirlo fuerte. Lo ya guardado sigue siendo valido.
        print(f"\n{'='*60}")
        print(f"CORRIDA ABORTADA: Google nos bloqueo ({e})")
        print(f"Fichas rescatadas antes del corte: {s.fichas_extraidas}")
        print("Espera unas horas o cambia de IP antes de reintentar.")
        print("El progreso quedo guardado: al relanzar retoma donde iba.")
        print('='*60)
        codigo = 3
    except KeyboardInterrupt:
        print(f"\nInterrumpido. {s.fichas_extraidas} fichas guardadas, progreso registrado.")
        codigo = 130
    finally:
        try:
            s.close()
        except Exception:
            pass

    r = registro.resumen()
    print(f"\nSesion: {s.fichas_extraidas} fichas nuevas en {args.salida}.csv")
    print(f"Acumulado historico: {r['fichas']} fichas en {r['combinaciones']} combinaciones")
    if not args.sin_historial:
        print(f"Historial de negocios unicos: {historial.negocios} (en {args.vistos})")
    return codigo


if __name__ == '__main__':
    sys.exit(main())
