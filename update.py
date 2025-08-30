#!/usr/bin/env python3
"""
Sistema de actualización automática para GMB Scraper Peru
"""

import subprocess
import sys
import os
import json
from datetime import datetime
import argparse

class GMBUpdater:
    def __init__(self):
        self.repo_url = "https://github.com/LucumaAgency/gmb-scrape.git"
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.version_file = os.path.join(self.current_dir, "version.json")
        
    def get_current_version(self):
        """Obtiene la versión actual del sistema"""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    return data.get('version', 'unknown')
            else:
                # Si no existe el archivo, obtener del git
                result = subprocess.run(
                    ['git', 'rev-parse', '--short', 'HEAD'],
                    capture_output=True, text=True, cwd=self.current_dir
                )
                if result.returncode == 0:
                    return result.stdout.strip()
        except:
            pass
        return "unknown"
    
    def check_git_installed(self):
        """Verifica si Git está instalado"""
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def check_for_updates(self):
        """Verifica si hay actualizaciones disponibles"""
        print("🔍 Verificando actualizaciones...")
        
        if not self.check_git_installed():
            print("❌ Git no está instalado. Instálalo primero:")
            print("   Ubuntu/Debian: sudo apt-get install git")
            print("   Windows: Descarga desde https://git-scm.com/")
            return False
        
        try:
            # Hacer fetch para obtener información del remoto
            subprocess.run(
                ['git', 'fetch', 'origin'],
                capture_output=True, cwd=self.current_dir
            )
            
            # Comparar local con remoto
            result = subprocess.run(
                ['git', 'rev-list', 'HEAD...origin/main', '--count'],
                capture_output=True, text=True, cwd=self.current_dir
            )
            
            updates_available = int(result.stdout.strip()) > 0
            
            if updates_available:
                # Obtener lista de cambios
                changes = subprocess.run(
                    ['git', 'log', 'HEAD..origin/main', '--oneline'],
                    capture_output=True, text=True, cwd=self.current_dir
                )
                print("\n📦 Actualizaciones disponibles:")
                print(changes.stdout)
                return True
            else:
                print("✅ Ya tienes la última versión")
                return False
                
        except Exception as e:
            print(f"❌ Error verificando actualizaciones: {e}")
            return False
    
    def backup_config(self):
        """Hace backup de archivos de configuración"""
        backup_files = ['config.json', 'settings.json']
        backup_dir = os.path.join(self.current_dir, 'backup')
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for file in backup_files:
            file_path = os.path.join(self.current_dir, file)
            if os.path.exists(file_path):
                backup_path = os.path.join(backup_dir, f"{file}.{timestamp}")
                subprocess.run(['cp', file_path, backup_path])
                print(f"📋 Backup creado: {backup_path}")
    
    def update(self, force=False):
        """Actualiza la aplicación"""
        print("\n🚀 Iniciando actualización...")
        
        # Verificar cambios locales no guardados
        if not force:
            status = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, cwd=self.current_dir
            )
            
            if status.stdout.strip():
                print("⚠️  Hay cambios locales no guardados:")
                print(status.stdout)
                response = input("\n¿Deseas continuar? Los cambios locales se perderán (s/n): ")
                if response.lower() != 's':
                    print("Actualización cancelada")
                    return False
        
        # Hacer backup de configuraciones
        self.backup_config()
        
        try:
            # Resetear cambios locales si es forzado
            if force:
                print("🔄 Reseteando cambios locales...")
                subprocess.run(
                    ['git', 'reset', '--hard', 'HEAD'],
                    cwd=self.current_dir, check=True
                )
            
            # Hacer pull de los cambios
            print("📥 Descargando actualizaciones...")
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                capture_output=True, text=True, cwd=self.current_dir
            )
            
            if result.returncode == 0:
                print("✅ Actualización completada exitosamente")
                
                # Actualizar archivo de versión
                self.update_version_file()
                
                # Verificar si hay nuevas dependencias
                self.check_dependencies()
                
                print("\n✨ El sistema ha sido actualizado")
                print("   Reinicia la aplicación para aplicar los cambios")
                return True
            else:
                print(f"❌ Error durante la actualización:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error durante la actualización: {e}")
            return False
    
    def update_version_file(self):
        """Actualiza el archivo de versión"""
        try:
            commit = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True, text=True, cwd=self.current_dir
            ).stdout.strip()
            
            date = subprocess.run(
                ['git', 'log', '-1', '--format=%cd', '--date=short'],
                capture_output=True, text=True, cwd=self.current_dir
            ).stdout.strip()
            
            version_data = {
                'version': commit,
                'date': date,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.version_file, 'w') as f:
                json.dump(version_data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  No se pudo actualizar el archivo de versión: {e}")
    
    def check_dependencies(self):
        """Verifica e instala nuevas dependencias si es necesario"""
        requirements_file = os.path.join(self.current_dir, 'requirements.txt')
        
        if os.path.exists(requirements_file):
            print("\n📦 Verificando dependencias...")
            try:
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '-r', requirements_file, '--quiet'],
                    cwd=self.current_dir
                )
                print("✅ Dependencias actualizadas")
            except Exception as e:
                print(f"⚠️  Error actualizando dependencias: {e}")
                print("   Ejecuta manualmente: pip install -r requirements.txt")
    
    def install_update_shortcut(self):
        """Crea un acceso directo para actualizar"""
        if sys.platform == "win32":
            # Crear archivo .bat para Windows
            bat_content = f"""@echo off
cd /d "{self.current_dir}"
python update.py
pause
"""
            bat_path = os.path.join(self.current_dir, "actualizar.bat")
            with open(bat_path, 'w') as f:
                f.write(bat_content)
            print(f"✅ Acceso directo creado: actualizar.bat")
            
        else:
            # Crear script .sh para Linux/Mac
            sh_content = f"""#!/bin/bash
cd "{self.current_dir}"
python3 update.py
read -p "Presiona Enter para continuar..."
"""
            sh_path = os.path.join(self.current_dir, "actualizar.sh")
            with open(sh_path, 'w') as f:
                f.write(sh_content)
            os.chmod(sh_path, 0o755)
            print(f"✅ Script de actualización creado: actualizar.sh")

def main():
    parser = argparse.ArgumentParser(description='Actualizar GMB Scraper Peru')
    parser.add_argument('--force', action='store_true', 
                       help='Forzar actualización (descarta cambios locales)')
    parser.add_argument('--check', action='store_true',
                       help='Solo verificar si hay actualizaciones')
    parser.add_argument('--install-shortcut', action='store_true',
                       help='Instalar acceso directo para actualizar')
    
    args = parser.parse_args()
    
    updater = GMBUpdater()
    
    print("="*50)
    print("🔄 GMB Scraper Peru - Sistema de Actualización")
    print("="*50)
    print(f"Versión actual: {updater.get_current_version()}")
    print()
    
    if args.install_shortcut:
        updater.install_update_shortcut()
        return
    
    if args.check:
        updater.check_for_updates()
    else:
        if updater.check_for_updates():
            response = input("\n¿Deseas actualizar ahora? (s/n): ")
            if response.lower() == 's':
                updater.update(force=args.force)
        else:
            print("\nPuedes forzar la reinstalación con: python update.py --force")

if __name__ == "__main__":
    main()