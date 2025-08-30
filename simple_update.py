#!/usr/bin/env python3
"""
Script simple de actualización para GMB Scraper
"""

import subprocess
import sys
import os

def main():
    print("="*50)
    print(" GMB Scraper - Actualización Simple")
    print("="*50)
    
    try:
        # Ejecutar git pull
        print("\n📥 Descargando actualizaciones...")
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            if "Already up to date" in result.stdout:
                print("\n✅ Ya tienes la última versión")
                print("\nSi el programa muestra una versión antigua:")
                print("1. Cierra completamente la aplicación")
                print("2. Vuelve a abrirla")
            else:
                print("\n✅ Actualización completada exitosamente!")
                print("\n🔄 Reinicia la aplicación para ver los cambios")
        else:
            print(f"\n❌ Error al actualizar:")
            print(result.stderr)
            print("\nIntenta ejecutar manualmente:")
            print("  git pull origin main")
            
    except FileNotFoundError:
        print("\n❌ Git no está instalado")
        print("Instala Git primero:")
        print("  Windows: https://git-scm.com/download/win")
        print("  Linux: sudo apt-get install git")
        print("  Mac: brew install git")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    
    input("\nPresiona Enter para cerrar...")

if __name__ == "__main__":
    main()