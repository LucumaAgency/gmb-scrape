#!/usr/bin/env python3
"""Convierte la salida del scraper al CSV que consume la cola comercial.

El scraper escribe su propio esquema (name, rating, review_count, ...), pero
`lucuma/comercial/generar-cola.py` lee otro (Origen, Nombre, WhatsApp, Web,
Email, Estado, ...). Este adaptador traduce entre los dos y, si el CSV destino
ya existe, agrega solo los negocios nuevos: nunca pisa el trabajo comercial ya
hecho (Estado, Fecha contacto, Notas).

Uso:
    python3 a_csv_comercial.py campana_gmb.json --salida ../gmb/inmobiliarias-lima.csv
    python3 a_csv_comercial.py campana_gmb.csv --servicio SEO
"""
import argparse
import csv
import json
import os
import re
import sys

# Esquema exacto de la cola comercial (lucuma/comercial/generar-cola.py)
COLUMNAS = ['Origen', 'Tipo', 'Fecha contacto', 'Nombre', 'Contacto', 'Rubro',
            'Ciudad', 'Zona', 'WhatsApp', 'Web', 'IG', 'FB', 'Email',
            '¿Tiene web?', 'Servicio ofrecido', 'Estado', 'Proximo seguimiento',
            'Valor', 'Notas']

VACIO = ('', 'N/A', None, 'No disponible')


def limpio(valor):
    if valor in VACIO:
        return ''
    # El pipe rompe las tablas markdown de COLA.md, y los nombres de Google
    # vienen llenos ("Estudio contable en Lima | S&M Contadores")
    return str(valor).replace('|', '-').strip()


def normalizar_telefono(bruto):
    """Deja el telefono peruano en formato compacto: 983 436 614 -> 983436614."""
    tel = limpio(bruto)
    if not tel:
        return ''
    digitos = re.sub(r'\D', '', tel)
    if digitos.startswith('51') and len(digitos) == 11:
        digitos = digitos[2:]
    return digitos or tel


def clave_negocio(nombre, telefono, web):
    """Identidad de un prospecto: telefono o dominio; si no hay, el nombre."""
    if telefono:
        return f"tel:{telefono}"
    web = limpio(web).lower()
    if web:
        dominio = re.sub(r'^https?://(www\.)?', '', web).split('/')[0]
        if dominio:
            return f"web:{dominio}"
    return f"nom:{limpio(nombre).lower()}"


def leer_entrada(ruta):
    if ruta.endswith('.json'):
        with open(ruta, encoding='utf-8') as f:
            return json.load(f)
    with open(ruta, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def a_fila(reg, servicio=''):
    telefono = normalizar_telefono(reg.get('phone'))
    web = limpio(reg.get('website'))

    rating = limpio(reg.get('rating'))
    reviews = limpio(reg.get('review_count'))
    notas = f"{rating}* ({reviews} reviews)" if rating else ''

    # Rubro: la categoria real de Google es mas util que el termino buscado
    rubro = limpio(reg.get('category')) or limpio(reg.get('search_keyword'))

    return {
        'Origen': 'GMB',
        'Tipo': 'Prospecto',
        'Fecha contacto': '',
        'Nombre': limpio(reg.get('name')),
        'Contacto': '',
        'Rubro': rubro,
        'Ciudad': limpio(reg.get('district')),
        'Zona': limpio(reg.get('province')) or limpio(reg.get('department')),
        'WhatsApp': telefono,
        'Web': web,
        'IG': '',
        'FB': '',
        'Email': limpio(reg.get('email')),
        '¿Tiene web?': 'Si' if web else 'No',
        'Servicio ofrecido': servicio,
        'Estado': 'Nuevo',
        'Proximo seguimiento': '',
        'Valor': '',
        'Notas': notas,
    }


def main():
    p = argparse.ArgumentParser(description='Salida del scraper -> CSV de la cola comercial')
    p.add_argument('entrada', help='campana_gmb.json o .csv del scraper')
    p.add_argument('--salida', default='prospectos-gmb.csv')
    p.add_argument('--servicio', default='', help='servicio a ofrecer (ej: SEO)')
    p.add_argument('--min-rating', type=float, default=0)
    p.add_argument('--solo-con-contacto', action='store_true',
                   help='descartar negocios sin telefono ni email')
    args = p.parse_args()

    if not os.path.exists(args.entrada):
        print(f"No existe {args.entrada}")
        return 1

    registros = leer_entrada(args.entrada)
    print(f"{len(registros)} fichas leidas de {args.entrada}")

    # Lo que ya esta en el CSV destino no se toca ni se repite
    existentes, claves_previas = [], set()
    if os.path.exists(args.salida):
        with open(args.salida, encoding='utf-8-sig') as f:
            existentes = list(csv.DictReader(f))
        for r in existentes:
            claves_previas.add(clave_negocio(r.get('Nombre'), r.get('WhatsApp'), r.get('Web')))
        print(f"{len(existentes)} prospectos ya en {args.salida} (se conservan tal cual)")

    nuevas, descartadas, repetidas = [], 0, 0
    vistas = set(claves_previas)

    for reg in registros:
        if not limpio(reg.get('name')):
            descartadas += 1
            continue

        try:
            if args.min_rating and float(reg.get('rating') or 0) < args.min_rating:
                descartadas += 1
                continue
        except (TypeError, ValueError):
            pass

        fila = a_fila(reg, args.servicio)

        if args.solo_con_contacto and not (fila['WhatsApp'] or fila['Email']):
            descartadas += 1
            continue

        clave = clave_negocio(fila['Nombre'], fila['WhatsApp'], fila['Web'])
        if clave in vistas:
            repetidas += 1
            continue

        vistas.add(clave)
        nuevas.append(fila)

    with open(args.salida, 'w', newline='', encoding='utf-8-sig') as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS, extrasaction='ignore')
        escritor.writeheader()
        for r in existentes:
            escritor.writerow({c: r.get(c, '') for c in COLUMNAS})
        escritor.writerows(nuevas)

    print(f"\n+{len(nuevas)} prospectos nuevos"
          f" · {repetidas} repetidos omitidos"
          f" · {descartadas} descartados por filtros")
    print(f"Total en {args.salida}: {len(existentes) + len(nuevas)}")

    con_email = sum(1 for r in nuevas if r['Email'])
    con_tel = sum(1 for r in nuevas if r['WhatsApp'])
    if nuevas:
        print(f"De los nuevos: {con_tel} con telefono, {con_email} con email")
    return 0


if __name__ == '__main__':
    sys.exit(main())
