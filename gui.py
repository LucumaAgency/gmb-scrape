#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import json
import os
import sys
from datetime import datetime
import queue
import logging

try:
    from gmb_scraper import GMBScraper
except ImportError:
    from gmb_scraper_lite import GMBScraper

from locations_peru import PERU_LOCATIONS

# Version del programa
VERSION = "1.1.2"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GMBScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"GMB Scraper Peru v{VERSION} - Interfaz Gráfica")
        self.root.geometry("900x700")
        
        self.root.configure(bg='#f0f0f0')
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.scraper = None
        self.search_thread = None
        self.results_queue = queue.Queue()
        self.selected_locations = []
        
        # Variables para tracking de selección actual
        self.current_dept = None
        self.current_prov = None
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="🔍 Google My Business Scraper Peru", 
                                font=('Arial', 16, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Extractor de datos de negocios con filtros avanzados",
                                  font=('Arial', 10))
        subtitle_label.pack()
        
        version_label = ttk.Label(header_frame, text=f"Versión {VERSION}",
                                 font=('Arial', 9, 'italic'), foreground='gray')
        version_label.pack()
        
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        main_frame.rowconfigure(1, weight=1)
        
        self.setup_search_tab(notebook)
        self.setup_filters_tab(notebook)
        self.setup_locations_tab(notebook)
        self.setup_results_tab(notebook)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.search_button = ttk.Button(control_frame, text="🚀 Iniciar Búsqueda", 
                                       command=self.start_search, style='Accent.TButton')
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="⏹ Detener", 
                                      command=self.stop_search, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.export_button = ttk.Button(control_frame, text="💾 Exportar Resultados", 
                                        command=self.export_results, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        self.update_button = ttk.Button(control_frame, text="🔄 Actualizar", 
                                       command=self.check_updates)
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, 
                                           maximum=100, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Listo para iniciar")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
    def setup_search_tab(self, notebook):
        search_frame = ttk.Frame(notebook, padding="10")
        notebook.add(search_frame, text="🔍 Búsqueda")
        
        ttk.Label(search_frame, text="Término de búsqueda:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.search_entry = ttk.Entry(search_frame, width=40, font=('Arial', 10))
        self.search_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        self.search_entry.insert(0, "restaurantes")
        
        ttk.Label(search_frame, text="Ejemplos: restaurantes, hoteles, gimnasios, clínicas", 
                 font=('Arial', 9, 'italic')).grid(row=2, column=0, sticky=tk.W)
        
        ttk.Separator(search_frame, orient='horizontal').grid(row=3, column=0, sticky=(tk.W, tk.E), pady=20)
        
        ttk.Label(search_frame, text="Opciones de búsqueda:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.headless_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(search_frame, text="Modo invisible (sin ventana del navegador)", 
                       variable=self.headless_var).grid(row=5, column=0, sticky=tk.W, pady=2)
        
        self.extract_emails_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(search_frame, text="Extraer emails de sitios web", 
                       variable=self.extract_emails_var).grid(row=6, column=0, sticky=tk.W, pady=2)
        
        self.incremental_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(search_frame, text="Guardado incremental (guarda después de cada ubicación)", 
                       variable=self.incremental_save_var).grid(row=7, column=0, sticky=tk.W, pady=2)
        
        ttk.Separator(search_frame, orient='horizontal').grid(row=8, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(search_frame, text="Paginación de resultados:", font=('Arial', 10, 'bold')).grid(row=9, column=0, sticky=tk.W, pady=5)
        
        # Frame para controles de paginación
        pagination_frame = ttk.Frame(search_frame)
        pagination_frame.grid(row=10, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(pagination_frame, text="Resultados por ubicación:").pack(side=tk.LEFT, padx=(0, 5))
        self.max_results_var = tk.IntVar(value=20)
        max_results_spinbox = ttk.Spinbox(pagination_frame, from_=10, to=100, increment=10, 
                                          textvariable=self.max_results_var, width=10)
        max_results_spinbox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(pagination_frame, text="Saltar primeros:").pack(side=tk.LEFT, padx=(20, 5))
        self.skip_results_var = tk.IntVar(value=0)
        skip_results_spinbox = ttk.Spinbox(pagination_frame, from_=0, to=500, increment=20, 
                                           textvariable=self.skip_results_var, width=10)
        skip_results_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Botones de paginación rápida
        pagination_buttons = ttk.Frame(search_frame)
        pagination_buttons.grid(row=11, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(pagination_buttons, text="Páginas rápidas:").pack(side=tk.LEFT, padx=(0, 10))
        
        def set_page(page_num):
            """Configura el offset basado en el número de página"""
            results_per_page = self.max_results_var.get()
            self.skip_results_var.set((page_num - 1) * results_per_page)
            
        ttk.Button(pagination_buttons, text="Página 1 (1-20)", 
                  command=lambda: set_page(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_buttons, text="Página 2 (21-40)", 
                  command=lambda: set_page(2)).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_buttons, text="Página 3 (41-60)", 
                  command=lambda: set_page(3)).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_buttons, text="Página 4 (61-80)", 
                  command=lambda: set_page(4)).pack(side=tk.LEFT, padx=2)
        
        # Texto de ayuda
        help_text = ("Ejemplo: Para obtener resultados 21-40, pon 'Saltar primeros: 20' y 'Resultados: 20'\n"
                    "O usa los botones de página rápida")
        ttk.Label(search_frame, text=help_text, font=('Arial', 8, 'italic'), 
                 foreground='gray').grid(row=12, column=0, sticky=tk.W, pady=5)
        
        search_frame.columnconfigure(0, weight=1)
        
    def setup_filters_tab(self, notebook):
        filters_frame = ttk.Frame(notebook, padding="10")
        notebook.add(filters_frame, text="⚙️ Filtros")
        
        ttk.Label(filters_frame, text="Filtros de calidad:", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(filters_frame, text="Rating mínimo (0-5):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.min_rating_var = tk.DoubleVar(value=0)
        rating_scale = ttk.Scale(filters_frame, from_=0, to=5, orient=tk.HORIZONTAL, 
                                 variable=self.min_rating_var, length=200)
        rating_scale.grid(row=1, column=1, pady=5)
        self.rating_label = ttk.Label(filters_frame, text="0.0")
        self.rating_label.grid(row=1, column=2, padx=5)
        rating_scale.configure(command=lambda v: self.rating_label.config(text=f"{float(v):.1f}"))
        
        ttk.Label(filters_frame, text="Mínimo de reseñas:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.min_reviews_var = tk.IntVar(value=0)
        ttk.Spinbox(filters_frame, from_=0, to=1000, increment=10, 
                   textvariable=self.min_reviews_var, width=15).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Separator(filters_frame, orient='horizontal').grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        ttk.Label(filters_frame, text="Filtros de antigüedad:", font=('Arial', 12, 'bold')).grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Label(filters_frame, text="Antigüedad mínima (días):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.min_age_var = tk.IntVar(value=0)
        ttk.Spinbox(filters_frame, from_=0, to=3650, increment=30, 
                   textvariable=self.min_age_var, width=15).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(filters_frame, text="Antigüedad máxima (días):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.max_age_var = tk.IntVar(value=36500)
        ttk.Spinbox(filters_frame, from_=0, to=36500, increment=365, 
                   textvariable=self.max_age_var, width=15).grid(row=6, column=1, sticky=tk.W, pady=5)
        
        self.apply_filters_button = ttk.Button(filters_frame, text="Aplicar Filtros", 
                                              command=self.apply_filters)
        self.apply_filters_button.grid(row=7, column=0, columnspan=2, pady=20)
        
    def setup_locations_tab(self, notebook):
        locations_frame = ttk.Frame(notebook, padding="10")
        notebook.add(locations_frame, text="📍 Ubicaciones")
        
        ttk.Label(locations_frame, text="Seleccione las ubicaciones para buscar:", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        paned = ttk.PanedWindow(locations_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        dept_frame = ttk.Frame(paned)
        paned.add(dept_frame, weight=1)
        
        ttk.Label(dept_frame, text="Departamentos:").pack()
        dept_scroll = ttk.Scrollbar(dept_frame)
        dept_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.dept_listbox = tk.Listbox(dept_frame, yscrollcommand=dept_scroll.set, 
                                       selectmode=tk.SINGLE, height=15)
        self.dept_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dept_scroll.config(command=self.dept_listbox.yview)
        
        for dept in PERU_LOCATIONS.keys():
            self.dept_listbox.insert(tk.END, dept)
        
        self.dept_listbox.bind('<<ListboxSelect>>', self.on_dept_select)
        
        prov_frame = ttk.Frame(paned)
        paned.add(prov_frame, weight=1)
        
        ttk.Label(prov_frame, text="Provincias:").pack()
        prov_scroll = ttk.Scrollbar(prov_frame)
        prov_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.prov_listbox = tk.Listbox(prov_frame, yscrollcommand=prov_scroll.set, 
                                       selectmode=tk.SINGLE, height=15)
        self.prov_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        prov_scroll.config(command=self.prov_listbox.yview)
        
        self.prov_listbox.bind('<<ListboxSelect>>', self.on_prov_select)
        
        dist_frame = ttk.Frame(paned)
        paned.add(dist_frame, weight=1)
        
        ttk.Label(dist_frame, text="Distritos:").pack()
        dist_scroll = ttk.Scrollbar(dist_frame)
        dist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.dist_listbox = tk.Listbox(dist_frame, yscrollcommand=dist_scroll.set, 
                                       selectmode=tk.MULTIPLE, height=15)
        self.dist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dist_scroll.config(command=self.dist_listbox.yview)
        
        button_frame = ttk.Frame(locations_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Agregar Seleccionados", 
                  command=self.add_locations).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar Selección", 
                  command=self.clear_locations).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Seleccionar Todos", 
                  command=self.select_all_locations).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(locations_frame, text="Ubicaciones seleccionadas:").pack(pady=(10, 5))
        
        self.selected_locations_text = scrolledtext.ScrolledText(locations_frame, height=5, width=60)
        self.selected_locations_text.pack()
        self.selected_locations_text.config(state=tk.DISABLED)
        
    def setup_results_tab(self, notebook):
        results_frame = ttk.Frame(notebook, padding="10")
        notebook.add(results_frame, text="📊 Resultados")
        
        stats_frame = ttk.Frame(results_frame)
        stats_frame.pack(pady=10)
        
        self.total_results_label = ttk.Label(stats_frame, text="Total de resultados: 0", 
                                            font=('Arial', 11, 'bold'))
        self.total_results_label.pack(side=tk.LEFT, padx=10)
        
        self.emails_found_label = ttk.Label(stats_frame, text="Con email: 0", 
                                           font=('Arial', 11, 'bold'))
        self.emails_found_label.pack(side=tk.LEFT, padx=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20, width=80)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
    def on_dept_select(self, event):
        """Maneja la selección de departamento y carga las provincias"""
        try:
            selection = self.dept_listbox.curselection()
            if not selection:
                print("DEBUG: No hay departamento seleccionado")
                return
                
            # Guardar el departamento seleccionado
            self.current_dept = self.dept_listbox.get(selection[0])
            print(f"\n>>> Departamento seleccionado: '{self.current_dept}'")
            
            # Limpiar listas
            self.prov_listbox.delete(0, tk.END)
            self.dist_listbox.delete(0, tk.END)
            
            # Resetear provincia actual
            self.current_prov = None
            
            # Cargar provincias
            if self.current_dept in PERU_LOCATIONS:
                provinces = list(PERU_LOCATIONS[self.current_dept].keys())
                print(f"    Cargando {len(provinces)} provincias")
                for prov in provinces:
                    self.prov_listbox.insert(tk.END, prov)
                print(f"    Provincias disponibles: {provinces[:5]}...")
            else:
                print(f"    ERROR: '{self.current_dept}' no encontrado en PERU_LOCATIONS")
                
        except Exception as e:
            print(f"❌ EXCEPCIÓN en on_dept_select: {e}")
            
    def on_prov_select(self, event):
        """Maneja la selección de provincia y carga los distritos"""
        try:
            # Debug detallado
            print("\n>>> EVENTO: on_prov_select disparado")
            
            # Obtener selección de provincia
            prov_selection = self.prov_listbox.curselection()
            
            print(f"    prov_selection: {prov_selection}")
            
            # Verificar que hay provincia seleccionada
            if len(prov_selection) == 0:
                print("    ⚠️ No hay provincia seleccionada")
                return
            
            # Usar el departamento guardado en la variable de instancia
            if not self.current_dept:
                print("    ⚠️ No hay departamento guardado en self.current_dept")
                # Intentar obtenerlo del listbox como fallback
                dept_selection = self.dept_listbox.curselection()
                if len(dept_selection) > 0:
                    self.current_dept = self.dept_listbox.get(dept_selection[0])
                    print(f"    Recuperado departamento del listbox: '{self.current_dept}'")
                else:
                    print("    ❌ No se puede determinar el departamento")
                    return
            
            # Obtener la provincia seleccionada
            prov = self.prov_listbox.get(prov_selection[0])
            self.current_prov = prov
            
            print(f"    Departamento (guardado): '{self.current_dept}'")
            print(f"    Provincia (seleccionada): '{prov}'")
            
            # Limpiar lista de distritos
            self.dist_listbox.delete(0, tk.END)
            
            # Verificar y cargar distritos
            if self.current_dept not in PERU_LOCATIONS:
                print(f"    ❌ ERROR: Departamento '{self.current_dept}' no encontrado en PERU_LOCATIONS")
                print(f"    Claves disponibles: {list(PERU_LOCATIONS.keys())[:10]}")
                return
            
            if prov not in PERU_LOCATIONS[self.current_dept]:
                print(f"    ❌ ERROR: Provincia '{prov}' no encontrada en PERU_LOCATIONS['{self.current_dept}']")
                print(f"    Provincias disponibles: {list(PERU_LOCATIONS[self.current_dept].keys())}")
                return
            
            # Cargar distritos
            districts = PERU_LOCATIONS[self.current_dept][prov]
            print(f"    ✅ Encontrados {len(districts)} distritos para {prov}, {self.current_dept}")
            
            # Insertar distritos ordenados
            districts_sorted = sorted(districts)
            for i, dist in enumerate(districts_sorted):
                self.dist_listbox.insert(tk.END, dist)
                if i < 5:  # Mostrar primeros 5 como confirmación
                    print(f"       {i+1}. {dist}")
            
            if len(districts) > 5:
                print(f"       ... y {len(districts)-5} más")
            
            print(f"    ✅ Distritos cargados en la lista")
            
        except Exception as e:
            print(f"\n❌ EXCEPCIÓN en on_prov_select:")
            print(f"    Error: {e}")
            print(f"    Tipo: {type(e)}")
            import traceback
            traceback.print_exc()
                
    def add_locations(self):
        """Agrega las ubicaciones seleccionadas a la lista"""
        print("\n>>> Intentando agregar ubicaciones...")
        
        # Obtener selecciones de distritos
        dist_selections = self.dist_listbox.curselection()
        
        # Verificar que tenemos departamento y provincia guardados
        if not self.current_dept:
            print("    ❌ No hay departamento seleccionado")
            messagebox.showwarning("Error", "Por favor seleccione un departamento primero")
            return
            
        if not self.current_prov:
            print("    ❌ No hay provincia seleccionada")
            messagebox.showwarning("Error", "Por favor seleccione una provincia primero")
            return
            
        if not dist_selections:
            print("    ❌ No hay distritos seleccionados")
            messagebox.showwarning("Error", "Por favor seleccione al menos un distrito")
            return
        
        # Usar las variables de instancia guardadas
        dept = self.current_dept
        prov = self.current_prov
        
        print(f"    Departamento: {dept}")
        print(f"    Provincia: {prov}")
        print(f"    Distritos seleccionados: {len(dist_selections)}")
        
        # Agregar cada distrito seleccionado
        added_count = 0
        for dist_idx in dist_selections:
            dist = self.dist_listbox.get(dist_idx)
            location = (dept, prov, dist)
            if location not in self.selected_locations:
                self.selected_locations.append(location)
                added_count += 1
                print(f"      ✓ Agregado: {dist}")
            else:
                print(f"      - Ya existe: {dist}")
        
        self.update_selected_locations_display()
        
        if added_count > 0:
            print(f"    ✅ {added_count} ubicaciones agregadas")
            messagebox.showinfo("Éxito", f"Se agregaron {added_count} ubicaciones")
        else:
            print("    ⚠️ Todas las ubicaciones ya estaban en la lista")
            messagebox.showinfo("Info", "Las ubicaciones seleccionadas ya están en la lista")
            
    def clear_locations(self):
        self.selected_locations = []
        self.update_selected_locations_display()
        
    def select_all_locations(self):
        self.selected_locations = []
        for dept in PERU_LOCATIONS:
            for prov in PERU_LOCATIONS[dept]:
                for dist in PERU_LOCATIONS[dept][prov]:
                    self.selected_locations.append((dept, prov, dist))
        self.update_selected_locations_display()
        
    def update_selected_locations_display(self):
        self.selected_locations_text.config(state=tk.NORMAL)
        self.selected_locations_text.delete(1.0, tk.END)
        
        for dept, prov, dist in self.selected_locations:
            self.selected_locations_text.insert(tk.END, f"• {dist}, {prov}, {dept}\n")
        
        self.selected_locations_text.config(state=tk.DISABLED)
        
    def apply_filters(self):
        messagebox.showinfo("Filtros", "Filtros aplicados correctamente")
        
    def start_search(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Error", "Por favor ingrese un término de búsqueda")
            return
            
        if not self.selected_locations:
            messagebox.showwarning("Error", "Por favor seleccione al menos una ubicación")
            return
            
        self.search_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.results_text.delete(1.0, tk.END)
        
        self.search_thread = threading.Thread(target=self.perform_search, args=(query,))
        self.search_thread.daemon = True
        self.search_thread.start()
        
        self.root.after(100, self.check_results_queue)
        
    def perform_search(self, query):
        try:
            print(f"\n{'='*60}")
            print(f"INICIANDO BÚSQUEDA")
            print(f"{'='*60}")
            print(f"Query: '{query}'")
            print(f"Modo headless: {self.headless_var.get()}")
            print(f"Total ubicaciones: {len(self.selected_locations)}")
            
            skip_first = self.skip_results_var.get()
            max_results = self.max_results_var.get()
            
            if skip_first > 0:
                print(f"Paginación: Saltando primeros {skip_first} resultados")
                print(f"Obteniendo resultados: {skip_first + 1} al {skip_first + max_results}")
            else:
                print(f"Obteniendo primeros {max_results} resultados")
            
            self.scraper = GMBScraper(headless=self.headless_var.get())
            print("✓ Scraper creado")
            
            self.scraper.init_driver()
            print("✓ Driver inicializado")
            
            filters = {
                'min_rating': self.min_rating_var.get(),
                'min_reviews': self.min_reviews_var.get(),
                'min_age_days': self.min_age_var.get(),
                'max_age_days': self.max_age_var.get()
            }
            print(f"Filtros: {filters}")
            
            # Generar nombre de archivo para esta sesión
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gmb_{query.replace(' ', '_')}_{timestamp}"
            
            print(f"Archivo de resultados: {filename}.csv / {filename}.json")
            print(f"Los resultados se guardarán automáticamente después de cada ubicación\n")
            
            total_locations = len(self.selected_locations)
            total_found = 0
            total_with_emails = 0
            first_batch = True  # Para saber si es el primer batch
            all_results = []  # Colectar todos los resultados
            
            for idx, (dept, prov, dist) in enumerate(self.selected_locations):
                if self.search_thread is None:
                    print("⚠️ Búsqueda detenida por el usuario")
                    break
                
                location_num = idx + 1
                print(f"\n[{location_num}/{total_locations}] Buscando en {dist}, {prov}, {dept}")
                
                progress = ((idx + 1) / total_locations) * 100
                self.results_queue.put(('progress', progress))
                self.results_queue.put(('status', f"Buscando en {dist}, {prov}..."))
                
                try:
                    # Pasar parámetros de paginación
                    results = self.scraper.search_location(
                        query, dept, prov, dist,
                        skip_first=skip_first,
                        max_results=max_results,
                        **filters
                    )
                    print(f"  → Encontrados: {len(results)} resultados")
                except Exception as e:
                    print(f"  ✗ Error en búsqueda: {e}")
                    results = []
                
                total_found += len(results)
                emails_found = sum(1 for r in results if r.get('email', 'N/A') != 'N/A')
                total_with_emails += emails_found
                
                # Agregar a la lista total
                all_results.extend(results)
                
                # Guardar resultados incrementalmente después de cada ubicación
                if results and self.incremental_save_var.get():
                    try:
                        # Determinar formato desde la GUI
                        format_to_save = self.format_var.get()
                        
                        self.scraper.save_results_incremental(
                            results, 
                            filename=filename, 
                            format=format_to_save,
                            append=not first_batch  # Create on first, append on rest
                        )
                        first_batch = False
                        print(f"  ✓ Resultados guardados incrementalmente (batch {location_num}/{total_locations})")
                        print(f"     Archivo: {filename}.{'csv/json' if format_to_save == 'both' else format_to_save}")
                    except Exception as save_error:
                        print(f"  ⚠️ Error al guardar batch: {save_error}")
                        import traceback
                        traceback.print_exc()
                
                result_text = f"\n{'='*60}\n"
                result_text += f"📍 {dist}, {prov}, {dept}\n"
                result_text += f"Encontrados: {len(results)} | Con email: {emails_found}\n"
                if self.incremental_save_var.get() and results:
                    result_text += f"Guardado: ✓ (incremental)\n"
                else:
                    result_text += f"Guardado: Pendiente (al final)\n"
                result_text += f"{'='*60}\n"
                
                for r in results:
                    result_text += f"\n📌 {r['name']}\n"
                    result_text += f"   ⭐ Rating: {r.get('rating', 'N/A')} ({r.get('reviews', 0)} reviews)\n"
                    result_text += f"   📧 Email: {r.get('email', 'N/A')}\n"
                    result_text += f"   📞 Teléfono: {r.get('phone', 'N/A')}\n"
                    result_text += f"   🌐 Web: {r.get('website', 'N/A')}\n"
                    result_text += f"   📍 Dirección: {r.get('address', 'N/A')}\n"
                
                self.results_queue.put(('result', result_text))
                self.results_queue.put(('stats', (total_found, total_with_emails)))
            
            print(f"\n{'='*60}")
            print(f"RESUMEN FINAL")
            print(f"{'='*60}")
            print(f"Total negocios encontrados: {total_found}")
            print(f"Total con email: {total_with_emails}")
            
            # Guardar todos los resultados si no se usó guardado incremental
            if not self.incremental_save_var.get() and all_results:
                try:
                    format_to_save = self.format_var.get()
                    self.scraper.save_results(all_results, filename=filename, format=format_to_save)
                    print(f"\n✅ Todos los resultados guardados en {filename}.{format_to_save if format_to_save != 'both' else 'csv/json'}")
                except Exception as save_error:
                    print(f"\n❌ Error al guardar resultados finales: {save_error}")
                    import traceback
                    traceback.print_exc()
            elif self.incremental_save_var.get():
                print(f"\n✅ Todos los resultados ya fueron guardados incrementalmente")
                print(f"Archivo: {filename}.{'csv/json' if self.format_var.get() == 'both' else self.format_var.get()}")
            
            self.results_queue.put(('complete', f"Búsqueda completada. Resultados en {filename}"))
            print(f"\n✅ BÚSQUEDA COMPLETADA")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n❌ ERROR EN BÚSQUEDA: {e}")
            print(f"Tipo de error: {type(e)}")
            import traceback
            traceback.print_exc()
            self.results_queue.put(('error', str(e)))
        finally:
            if self.scraper:
                self.scraper.close()
                
    def check_results_queue(self):
        try:
            while True:
                msg_type, msg_data = self.results_queue.get_nowait()
                
                if msg_type == 'progress':
                    self.progress_var.set(msg_data)
                elif msg_type == 'status':
                    self.status_label.config(text=msg_data)
                elif msg_type == 'result':
                    self.results_text.insert(tk.END, msg_data)
                    self.results_text.see(tk.END)
                elif msg_type == 'stats':
                    total, with_email = msg_data
                    self.total_results_label.config(text=f"Total de resultados: {total}")
                    self.emails_found_label.config(text=f"Con email: {with_email}")
                elif msg_type == 'complete':
                    self.status_label.config(text=msg_data)
                    self.search_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    self.export_button.config(state=tk.NORMAL)
                    messagebox.showinfo("Completado", msg_data)
                    return
                elif msg_type == 'error':
                    messagebox.showerror("Error", msg_data)
                    self.search_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    return
                    
        except queue.Empty:
            pass
            
        if self.search_thread and self.search_thread.is_alive():
            self.root.after(100, self.check_results_queue)
            
    def stop_search(self):
        if self.search_thread:
            self.search_thread = None
            self.status_label.config(text="Búsqueda detenida")
            self.search_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
    def export_results(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            messagebox.showinfo("Exportar", f"Resultados exportados a {file_path}")
    
    def check_updates(self):
        """Verificar y aplicar actualizaciones"""
        import subprocess
        
        # Primero verificar si hay actualizaciones disponibles
        result = messagebox.askyesno(
            "Actualizar", 
            f"Versión actual: {VERSION}\n\n"
            "¿Deseas verificar si hay actualizaciones disponibles?\n\n"
            "Nota: Si acabas de actualizar manualmente con git pull,\n"
            "necesitas reiniciar la aplicación para ver los cambios."
        )
        
        if result:
            try:
                # Mostrar mensaje de actualización
                messagebox.showinfo(
                    "Actualizando",
                    "Se ejecutará el actualizador.\n\n"
                    "1. Cierra esta ventana\n"
                    "2. Ejecuta en terminal: git pull origin main\n"
                    "3. Vuelve a abrir la aplicación\n\n"
                    "O usa: python update.py"
                )
                
                # Intentar ejecutar git pull directamente
                try:
                    result = subprocess.run(
                        ["git", "pull", "origin", "main"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        if "Already up to date" in result.stdout:
                            messagebox.showinfo(
                                "Sin actualizaciones",
                                "Ya tienes la última versión.\n\n"
                                "Si acabas de actualizar, reinicia la aplicación."
                            )
                        else:
                            messagebox.showinfo(
                                "Actualización completada",
                                "Se descargaron nuevas actualizaciones.\n\n"
                                "Reinicia la aplicación para aplicar los cambios."
                            )
                            self.on_closing()
                    else:
                        error_msg = result.stderr if result.stderr else "Error desconocido"
                        messagebox.showwarning(
                            "Actualización manual",
                            f"No se pudo actualizar automáticamente.\n\n"
                            "Ejecuta en terminal:\n"
                            "git pull origin main\n\n"
                            f"Error: {error_msg}"
                        )
                except subprocess.TimeoutExpired:
                    messagebox.showwarning(
                        "Timeout",
                        "La actualización tardó demasiado.\n"
                        "Intenta actualizar manualmente:\n"
                        "git pull origin main"
                    )
                except FileNotFoundError:
                    messagebox.showwarning(
                        "Git no encontrado",
                        "Git no está instalado o no está en el PATH.\n\n"
                        "Actualiza manualmente con:\n"
                        "git pull origin main"
                    )
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error durante la actualización:\n{e}")
            
    def on_closing(self):
        if self.scraper:
            self.scraper.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = GMBScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()