#!/usr/bin/env python3
"""
Instalador para GMB Scraper Peru - Windows
Este script configura el entorno y las dependencias necesarias
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import threading


class InstallerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GMB Scraper Peru - Instalador")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title = ttk.Label(main_frame, text="GMB Scraper Peru - Instalador", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=10)
        
        subtitle = ttk.Label(main_frame, text="Instalación del extractor de datos de Google My Business",
                           font=('Arial', 10))
        subtitle.pack(pady=5)
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=20)
        
        self.status_label = ttk.Label(main_frame, text="Presione 'Instalar' para comenzar",
                                    font=('Arial', 10))
        self.status_label.pack(pady=10)
        
        self.progress = ttk.Progressbar(main_frame, mode='determinate', length=400)
        self.progress.pack(pady=20)
        
        self.log_text = tk.Text(main_frame, height=10, width=70)
        self.log_text.pack(pady=10)
        
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.install_button = ttk.Button(button_frame, text="Instalar", 
                                        command=self.start_installation)
        self.install_button.pack(side=tk.LEFT, padx=10)
        
        self.close_button = ttk.Button(button_frame, text="Cerrar", 
                                      command=self.root.quit)
        self.close_button.pack(side=tk.LEFT, padx=10)
        
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update()
        
    def start_installation(self):
        self.install_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.install)
        thread.daemon = True
        thread.start()
        
    def install(self):
        try:
            total_steps = 7
            current_step = 0
            
            self.status_label.config(text="Verificando Python...")
            self.log("Verificando instalación de Python...")
            current_step += 1
            self.update_progress((current_step / total_steps) * 100)
            
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
                self.log("❌ Se requiere Python 3.8 o superior")
                messagebox.showerror("Error", "Se requiere Python 3.8 o superior")
                return
            
            self.log(f"✓ Python {python_version.major}.{python_version.minor} detectado")
            
            self.status_label.config(text="Instalando pip...")
            self.log("Verificando pip...")
            current_step += 1
            self.update_progress((current_step / total_steps) * 100)
            
            try:
                import pip
                self.log("✓ pip ya está instalado")
            except ImportError:
                self.log("Instalando pip...")
                subprocess.run([sys.executable, "-m", "ensurepip"], check=True)
                self.log("✓ pip instalado")
            
            self.status_label.config(text="Actualizando pip...")
            self.log("Actualizando pip...")
            current_step += 1
            self.update_progress((current_step / total_steps) * 100)
            
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         capture_output=True, text=True)
            self.log("✓ pip actualizado")
            
            self.status_label.config(text="Instalando dependencias...")
            self.log("Instalando dependencias de Python...")
            current_step += 1
            self.update_progress((current_step / total_steps) * 100)
            
            requirements = [
                "selenium>=4.15.0",
                "webdriver-manager>=4.0.0",
                "pandas>=2.0.0",
                "python-dateutil>=2.8.0",
                "tqdm>=4.66.0",
                "beautifulsoup4>=4.12.0",
                "requests>=2.31.0",
                "openpyxl>=3.1.0",
                "lxml>=4.9.0"
            ]
            
            for req in requirements:
                self.log(f"  Instalando {req.split('>=')[0]}...")
                result = subprocess.run([sys.executable, "-m", "pip", "install", req], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.log(f"  ✓ {req.split('>=')[0]} instalado")
                else:
                    self.log(f"  ⚠ Advertencia al instalar {req.split('>=')[0]}")
            
            self.status_label.config(text="Descargando ChromeDriver...")
            self.log("Configurando ChromeDriver...")
            current_step += 1
            self.update_progress((current_step / total_steps) * 100)
            
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                
                driver_path = ChromeDriverManager().install()
                self.log(f"✓ ChromeDriver instalado en: {driver_path}")
            except Exception as e:
                self.log(f"⚠ No se pudo instalar ChromeDriver automáticamente: {e}")
                self.log("  Será descargado cuando se ejecute el programa por primera vez")
            
            self.status_label.config(text="Creando accesos directos...")
            self.log("Creando accesos directos...")
            current_step += 1
            self.update_progress((current_step / total_steps) * 100)
            
            desktop = Path.home() / "Desktop"
            if desktop.exists():
                shortcut_content = f"""@echo off
cd /d "{os.getcwd()}"
python gui.py
pause"""
                
                shortcut_file = desktop / "GMB Scraper Peru.bat"
                with open(shortcut_file, 'w') as f:
                    f.write(shortcut_content)
                
                self.log(f"✓ Acceso directo creado en el escritorio")
            
            start_menu = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            if start_menu.exists():
                shortcut_file = start_menu / "GMB Scraper Peru.bat"
                with open(shortcut_file, 'w') as f:
                    f.write(shortcut_content)
                
                self.log("✓ Acceso directo creado en el menú inicio")
            
            self.status_label.config(text="Verificando instalación...")
            self.log("Verificando que todo esté correctamente instalado...")
            current_step += 1
            self.update_progress((current_step / total_steps) * 100)
            
            test_imports = [
                "selenium",
                "pandas",
                "bs4",
                "requests",
                "tqdm"
            ]
            
            all_ok = True
            for module in test_imports:
                try:
                    __import__(module)
                    self.log(f"  ✓ {module} funcionando")
                except ImportError:
                    self.log(f"  ❌ Error al importar {module}")
                    all_ok = False
            
            current_step += 1
            self.update_progress(100)
            
            if all_ok:
                self.status_label.config(text="¡Instalación completada con éxito!")
                self.log("\n" + "="*50)
                self.log("✅ INSTALACIÓN COMPLETADA CON ÉXITO")
                self.log("="*50)
                self.log("\nPara ejecutar el programa:")
                self.log("1. Use el acceso directo en el escritorio")
                self.log("2. O ejecute: python gui.py")
                self.log("\nPara usar desde línea de comandos:")
                self.log("python main.py --help")
                
                messagebox.showinfo("Éxito", "Instalación completada con éxito!\n\nPuede ejecutar el programa desde el acceso directo en el escritorio.")
            else:
                self.status_label.config(text="Instalación completada con advertencias")
                self.log("\n⚠ Instalación completada con algunas advertencias")
                self.log("El programa puede funcionar, pero revise los errores arriba")
                
        except Exception as e:
            self.status_label.config(text="Error durante la instalación")
            self.log(f"\n❌ Error durante la instalación: {str(e)}")
            messagebox.showerror("Error", f"Error durante la instalación:\n{str(e)}")
        finally:
            self.install_button.config(state=tk.NORMAL)
            
    def run(self):
        self.root.mainloop()


def main():
    if sys.platform != "win32":
        print("Este instalador es solo para Windows.")
        print("Para Linux/Mac, use: ./installer_linux.sh")
        sys.exit(1)
    
    installer = InstallerGUI()
    installer.run()


if __name__ == "__main__":
    main()