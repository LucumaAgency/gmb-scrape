#!/usr/bin/env python3
"""Test para verificar eventos de GUI"""

import tkinter as tk
from tkinter import ttk
from locations_peru import PERU_LOCATIONS

class TestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Test - Eventos de Selección")
        self.root.geometry("800x600")
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear 3 columnas
        # Departamentos
        dept_frame = ttk.LabelFrame(main_frame, text="Departamentos")
        dept_frame.grid(row=0, column=0, padx=5, sticky="nsew")
        
        self.dept_listbox = tk.Listbox(dept_frame, height=20)
        self.dept_listbox.pack(fill=tk.BOTH, expand=True)
        
        for dept in sorted(PERU_LOCATIONS.keys()):
            self.dept_listbox.insert(tk.END, dept)
        
        self.dept_listbox.bind('<<ListboxSelect>>', self.on_dept_select)
        
        # Provincias
        prov_frame = ttk.LabelFrame(main_frame, text="Provincias")
        prov_frame.grid(row=0, column=1, padx=5, sticky="nsew")
        
        self.prov_listbox = tk.Listbox(prov_frame, height=20)
        self.prov_listbox.pack(fill=tk.BOTH, expand=True)
        
        self.prov_listbox.bind('<<ListboxSelect>>', self.on_prov_select)
        
        # Distritos
        dist_frame = ttk.LabelFrame(main_frame, text="Distritos")
        dist_frame.grid(row=0, column=2, padx=5, sticky="nsew")
        
        self.dist_listbox = tk.Listbox(dist_frame, height=20)
        self.dist_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Area de debug
        debug_frame = ttk.LabelFrame(main_frame, text="Debug Output")
        debug_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")
        
        self.debug_text = tk.Text(debug_frame, height=8, width=80)
        self.debug_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        self.log("Aplicación iniciada. Selecciona un departamento.")
        
    def log(self, message):
        """Agregar mensaje al área de debug"""
        self.debug_text.insert(tk.END, f"{message}\n")
        self.debug_text.see(tk.END)
        print(message)  # También imprimir en consola
        
    def on_dept_select(self, event):
        selection = self.dept_listbox.curselection()
        if not selection:
            self.log("on_dept_select: No hay selección")
            return
            
        dept = self.dept_listbox.get(selection[0])
        self.log(f"\n>>> DEPARTAMENTO seleccionado: '{dept}'")
        
        # Limpiar listas
        self.prov_listbox.delete(0, tk.END)
        self.dist_listbox.delete(0, tk.END)
        
        if dept in PERU_LOCATIONS:
            provinces = list(PERU_LOCATIONS[dept].keys())
            self.log(f"  - Encontradas {len(provinces)} provincias")
            for prov in provinces:
                self.prov_listbox.insert(tk.END, prov)
            self.log(f"  - Provincias: {provinces}")
        else:
            self.log(f"  ERROR: '{dept}' no está en PERU_LOCATIONS")
            
    def on_prov_select(self, event):
        dept_selection = self.dept_listbox.curselection()
        prov_selection = self.prov_listbox.curselection()
        
        if not dept_selection:
            self.log("on_prov_select: No hay departamento seleccionado")
            return
        if not prov_selection:
            self.log("on_prov_select: No hay provincia seleccionada")
            return
            
        dept = self.dept_listbox.get(dept_selection[0])
        prov = self.prov_listbox.get(prov_selection[0])
        
        self.log(f"\n>>> PROVINCIA seleccionada: '{prov}' (en {dept})")
        
        # Limpiar distritos
        self.dist_listbox.delete(0, tk.END)
        
        if dept in PERU_LOCATIONS:
            if prov in PERU_LOCATIONS[dept]:
                districts = PERU_LOCATIONS[dept][prov]
                self.log(f"  - Encontrados {len(districts)} distritos")
                for dist in sorted(districts):
                    self.dist_listbox.insert(tk.END, dist)
                self.log(f"  - Primeros 5: {sorted(districts)[:5]}")
            else:
                self.log(f"  ERROR: '{prov}' no está en PERU_LOCATIONS['{dept}']")
                self.log(f"  Provincias disponibles: {list(PERU_LOCATIONS[dept].keys())}")
        else:
            self.log(f"  ERROR: '{dept}' no está en PERU_LOCATIONS")

def main():
    root = tk.Tk()
    app = TestGUI(root)
    
    # Auto-seleccionar Lima para testing
    root.after(100, lambda: app.dept_listbox.selection_set(14))  # Lima está en posición ~14
    root.after(200, lambda: app.dept_listbox.event_generate('<<ListboxSelect>>'))
    
    try:
        root.mainloop()
    except:
        print("No hay display disponible")
        # Hacer test sin GUI
        print("\n=== Test sin GUI ===")
        dept = "Lima"
        prov = "Lima"
        if dept in PERU_LOCATIONS and prov in PERU_LOCATIONS[dept]:
            print(f"✓ {dept}/{prov} tiene {len(PERU_LOCATIONS[dept][prov])} distritos")
        else:
            print(f"✗ Error con {dept}/{prov}")

if __name__ == "__main__":
    main()