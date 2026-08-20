#!/usr/bin/env python3
"""Registro de progreso para corridas largas: que combinaciones ya se hicieron.

Sin esto, una corrida interrumpida (bloqueo, corte, Ctrl+C) obliga a repetir
todo desde cero, lo que ademas quema busquedas contra Google innecesariamente.

Formato: un JSONL, una linea por combinacion terminada. Se puede leer a ojo y
sobrevive a que el proceso muera a mitad de escritura (solo se pierde la ultima
linea, no el archivo).
"""
import json
import os
from datetime import datetime


class RegistroProgreso:
    def __init__(self, ruta='progreso.jsonl'):
        self.ruta = ruta
        self.hechas = {}
        self._cargar()

    @staticmethod
    def clave(rubro, department, province, district):
        return f"{rubro}|{department}|{province}|{district}".lower()

    def _cargar(self):
        if not os.path.exists(self.ruta):
            return
        with open(self.ruta, encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    reg = json.loads(linea)
                except json.JSONDecodeError:
                    continue  # linea a medias de una corrida cortada
                if reg.get('clave'):
                    self.hechas[reg['clave']] = reg

    def ya_hecha(self, rubro, department, province, district):
        """Solo cuenta como hecha si termino completa.

        Una combinacion cortada por el tope de sesion queda 'parcial' y se
        vuelve a intentar en la siguiente corrida; si no, se perderian las
        fichas que faltaban por extraer.
        """
        reg = self.hechas.get(self.clave(rubro, department, province, district))
        return bool(reg) and reg.get('estado') == 'ok'

    def marcar(self, rubro, department, province, district, encontrados, estado='ok'):
        reg = {
            'clave': self.clave(rubro, department, province, district),
            'rubro': rubro,
            'departamento': department,
            'provincia': province,
            'distrito': district,
            'encontrados': encontrados,
            'estado': estado,
            'timestamp': datetime.now().isoformat(),
        }
        self.hechas[reg['clave']] = reg
        with open(self.ruta, 'a', encoding='utf-8') as f:
            f.write(json.dumps(reg, ensure_ascii=False) + '\n')
            f.flush()
            os.fsync(f.fileno())  # que sobreviva a un corte
        return reg

    def resumen(self):
        total = len(self.hechas)
        fichas = sum(r.get('encontrados', 0) for r in self.hechas.values())
        vacias = sum(1 for r in self.hechas.values() if not r.get('encontrados'))
        return {'combinaciones': total, 'fichas': fichas, 'sin_resultados': vacias}


class HistorialVistos:
    """Todos los negocios ya extraidos, de todas las corridas de todos los dias.

    Es lo que evita re-scrapear lo mismo la semana que viene. Se carga y se
    actualiza solo: no depende de que nadie se acuerde de pasar un flag.

    Guarda dos claves por negocio, el place_id y nombre|direccion, porque
    alguna ficha puede no tener place_id legible.
    """

    def __init__(self, ruta='vistos.jsonl'):
        self.ruta = ruta
        self.claves = set()
        self.negocios = 0
        self._cargar()

    @staticmethod
    def claves_de(reg):
        claves = set()
        if reg.get('place_id'):
            claves.add(reg['place_id'])
        nombre = (reg.get('name') or reg.get('Nombre') or '').strip()
        direccion = (reg.get('address') or '').strip()
        if nombre:
            claves.add(f"{nombre}|{direccion}".lower())
        return claves

    def _cargar(self):
        if not os.path.exists(self.ruta):
            return
        with open(self.ruta, encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    reg = json.loads(linea)
                except json.JSONDecodeError:
                    continue
                self.claves.update(reg.get('claves', []))
                self.negocios += 1

    def agregar(self, registros):
        """Anota negocios recien extraidos. Devuelve cuantos eran nuevos."""
        nuevos = 0
        with open(self.ruta, 'a', encoding='utf-8') as f:
            for reg in registros:
                claves = self.claves_de(reg)
                if not claves or claves & self.claves:
                    continue
                self.claves.update(claves)
                self.negocios += 1
                nuevos += 1
                f.write(json.dumps({
                    'claves': sorted(claves),
                    'nombre': reg.get('name') or reg.get('Nombre', ''),
                    'distrito': reg.get('district', ''),
                    'rubro': reg.get('search_keyword', ''),
                    'timestamp': datetime.now().isoformat(),
                }, ensure_ascii=False) + '\n')
            f.flush()
            os.fsync(f.fileno())
        return nuevos
