# GMB Scraper Peru - Guía de Instalación

## 🚀 Instalación Rápida

### Windows
```bash
python installer_windows.py
```

### Linux/Mac
```bash
chmod +x installer_linux.sh
./installer_linux.sh
```

## 📋 Requisitos Previos

- Python 3.8 o superior
- Google Chrome instalado
- Conexión a Internet

## 💻 Instalación Manual

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar la interfaz gráfica
```bash
python gui.py
```

### 3. Ejecutar desde línea de comandos
```bash
python main.py restaurantes --departments Lima
```

## 🎯 Características

- ✅ Interfaz gráfica intuitiva
- ✅ Búsqueda por ubicación (departamento, provincia, distrito)
- ✅ Filtros avanzados (rating, reviews, antigüedad)
- ✅ Extracción de emails desde sitios web
- ✅ Exportación a CSV y JSON
- ✅ Modo headless (sin ventana del navegador)
- ✅ Instaladores automatizados para Windows y Linux/Mac

## 🔧 Solución de Problemas

### Error: No module named 'tkinter'
**Linux:**
```bash
sudo apt-get install python3-tk
```

**Mac:**
```bash
brew install python-tk
```

### Error: Chrome driver not found
El instalador descarga automáticamente ChromeDriver. Si hay problemas:
```bash
pip install --upgrade webdriver-manager
```

### Error en Windows: Python no reconocido
1. Descarga Python desde: https://www.python.org/downloads/
2. Durante la instalación, marca "Add Python to PATH"
3. Reinicia el terminal y ejecuta el instalador

## 📝 Uso de la Interfaz Gráfica

1. **Búsqueda:** Ingresa el término (ej: restaurantes, hoteles)
2. **Ubicaciones:** Selecciona departamentos, provincias y distritos
3. **Filtros:** Configura rating mínimo, reviews, antigüedad
4. **Opciones:** Activa modo invisible y extracción de emails
5. **Iniciar:** Presiona el botón "Iniciar Búsqueda"
6. **Resultados:** Revisa los datos extraídos y exporta

## 🛠️ Uso desde Línea de Comandos

### Ejemplos básicos:
```bash
# Buscar restaurantes en Lima
python main.py restaurantes --departments Lima

# Buscar hoteles con filtros
python main.py hoteles --min-rating 4.0 --min-reviews 50

# Modo headless con exportación específica
python main.py gimnasios --headless --format csv

# Usar archivo de configuración
python main.py clinicas --config config.json
```

### Parámetros disponibles:
- `query`: Término de búsqueda (requerido)
- `--departments`: Departamentos a buscar
- `--provinces`: Provincias a buscar
- `--districts`: Distritos a buscar
- `--min-rating`: Rating mínimo (0-5)
- `--min-reviews`: Cantidad mínima de reviews
- `--min-age`: Antigüedad mínima en días
- `--max-age`: Antigüedad máxima en días
- `--output`: Nombre del archivo de salida
- `--format`: Formato de salida (csv, json, both)
- `--headless`: Ejecutar sin mostrar navegador
- `--config`: Archivo de configuración JSON

## 📂 Estructura de Archivos

```
gmb-scraper-peru/
├── gui.py                    # Interfaz gráfica
├── main.py                   # CLI principal
├── gmb_scraper.py           # Motor de scraping
├── gmb_scraper_lite.py      # Versión lite sin undetected-chromedriver
├── locations_peru.py        # Base de datos de ubicaciones
├── installer_windows.py     # Instalador Windows
├── installer_linux.sh       # Instalador Linux/Mac
├── requirements.txt         # Dependencias Python
└── README_INSTALACION.md   # Esta guía
```

## 🤝 Soporte

Para reportar problemas o solicitar características, contacta al desarrollador.