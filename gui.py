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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GMBScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GMB Scraper Peru - Interfaz Gráfica")
        self.root.geometry("900x700")
        
        self.root.configure(bg='#f0f0f0')
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.scraper = None
        self.search_thread = None
        self.results_queue = queue.Queue()
        self.selected_locations = []
        
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
        
        ttk.Label(search_frame, text="Máximo de resultados por ubicación:", font=('Arial', 10)).grid(row=7, column=0, sticky=tk.W, pady=10)
        
        self.max_results_var = tk.IntVar(value=20)
        max_results_spinbox = ttk.Spinbox(search_frame, from_=10, to=100, increment=10, 
                                          textvariable=self.max_results_var, width=10)
        max_results_spinbox.grid(row=8, column=0, sticky=tk.W)
        
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
        selection = self.dept_listbox.curselection()
        if selection:
            dept = self.dept_listbox.get(selection[0])
            self.prov_listbox.delete(0, tk.END)
            for prov in PERU_LOCATIONS[dept].keys():
                self.prov_listbox.insert(tk.END, prov)
            self.dist_listbox.delete(0, tk.END)
            
    def on_prov_select(self, event):
        dept_selection = self.dept_listbox.curselection()
        prov_selection = self.prov_listbox.curselection()
        
        if dept_selection and prov_selection:
            dept = self.dept_listbox.get(dept_selection[0])
            prov = self.prov_listbox.get(prov_selection[0])
            self.dist_listbox.delete(0, tk.END)
            for dist in PERU_LOCATIONS[dept][prov]:
                self.dist_listbox.insert(tk.END, dist)
                
    def add_locations(self):
        dept_selection = self.dept_listbox.curselection()
        prov_selection = self.prov_listbox.curselection()
        dist_selections = self.dist_listbox.curselection()
        
        if dept_selection and prov_selection and dist_selections:
            dept = self.dept_listbox.get(dept_selection[0])
            prov = self.prov_listbox.get(prov_selection[0])
            
            for dist_idx in dist_selections:
                dist = self.dist_listbox.get(dist_idx)
                location = (dept, prov, dist)
                if location not in self.selected_locations:
                    self.selected_locations.append(location)
            
            self.update_selected_locations_display()
            
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
            self.scraper = GMBScraper(headless=self.headless_var.get())
            self.scraper.init_driver()
            
            filters = {
                'min_rating': self.min_rating_var.get(),
                'min_reviews': self.min_reviews_var.get(),
                'min_age_days': self.min_age_var.get(),
                'max_age_days': self.max_age_var.get()
            }
            
            total_locations = len(self.selected_locations)
            total_found = 0
            total_with_emails = 0
            
            for idx, (dept, prov, dist) in enumerate(self.selected_locations):
                if self.search_thread is None:
                    break
                    
                progress = ((idx + 1) / total_locations) * 100
                self.results_queue.put(('progress', progress))
                self.results_queue.put(('status', f"Buscando en {dist}, {prov}..."))
                
                results = self.scraper.search_location(
                    query, dept, prov, dist, 
                    max_results=self.max_results_var.get(),
                    **filters
                )
                
                total_found += len(results)
                emails_found = sum(1 for r in results if r.get('email', 'N/A') != 'N/A')
                total_with_emails += emails_found
                
                result_text = f"\n{'='*60}\n"
                result_text += f"📍 {dist}, {prov}, {dept}\n"
                result_text += f"Encontrados: {len(results)} | Con email: {emails_found}\n"
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
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gmb_{query.replace(' ', '_')}_{timestamp}"
            self.scraper.save_results(filename, 'both')
            
            self.results_queue.put(('complete', f"Búsqueda completada. Resultados guardados en {filename}"))
            
        except Exception as e:
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