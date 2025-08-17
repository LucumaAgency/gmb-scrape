#!/usr/bin/env python3
"""
Ejemplo de uso de la funcionalidad Skip/Pagination
Para continuar extrayendo desde donde dejaste
"""

import subprocess
import time

def run_batch(query, location, batch_size=5, total_batches=4):
    """
    Ejecuta extracción en lotes con skip automático
    """
    print(f"🔄 Iniciando extracción en lotes de {batch_size} resultados")
    print(f"📍 Búsqueda: '{query}' en {location}")
    print(f"📊 Total a extraer: {batch_size * total_batches} resultados\n")
    
    for batch in range(total_batches):
        skip = batch * batch_size
        
        print(f"\n{'='*50}")
        print(f"LOTE {batch + 1}/{total_batches}")
        print(f"Extrayendo resultados {skip + 1} a {skip + batch_size}")
        print(f"{'='*50}")
        
        # Construir comando
        cmd = [
            'python', 'gmb_scraper_fast.py',
            query,
            '--locations', location,
            '--max-results', str(batch_size),
            '--skip', str(skip),
            '--append'  # Agregar al mismo archivo
        ]
        
        # Ejecutar
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Lote {batch + 1} completado")
            
            # Pausa entre lotes (para evitar detección)
            if batch < total_batches - 1:
                wait_time = 30  # segundos
                print(f"⏳ Esperando {wait_time} segundos antes del siguiente lote...")
                time.sleep(wait_time)
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en lote {batch + 1}: {e}")
            break
    
    print(f"\n{'='*50}")
    print("✨ EXTRACCIÓN COMPLETA")
    print(f"Resultados guardados en: gmb_fast_continuous.csv")
    print(f"{'='*50}")

if __name__ == "__main__":
    # Ejemplo: Extraer 20 restaurantes en lotes de 5
    run_batch(
        query="restaurantes",
        location="Miraflores",
        batch_size=5,      # 5 resultados por lote
        total_batches=4    # 4 lotes = 20 resultados total
    )