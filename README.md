# Google My Business Scraper - Perú 🇵🇪

Un scraper completo para extraer información de negocios de Google My Business en Perú, con capacidad de filtrado por ubicación geográfica, calificaciones, antigüedad y **extracción automática de emails**.

## 🚀 Características

### Información Extraída
- ✅ Nombre del negocio
- ✅ Rating (estrellas)
- ✅ Cantidad de reviews
- ✅ Dirección completa
- ✅ Teléfono
- ✅ Sitio web
- ✅ **Emails** (desde GMB y sitio web)
- ✅ Categoría
- ✅ Horarios
- ✅ Antigüedad estimada

### Filtros Disponibles
- 📍 **Ubicación**: Departamento, Provincia, Distrito
- ⭐ **Rating mínimo**: Filtrar por calificación
- 💬 **Reviews mínimos**: Filtrar por popularidad
- 📅 **Antigüedad**: Rango de días desde creación

### Extracción de Emails
El scraper busca emails en múltiples fuentes:
- Información visible en GMB
- Sitio web del negocio (si existe)
- Páginas de contacto
- Enlaces mailto
- Meta tags y texto HTML

## 📦 Instalación

```bash
# Clonar el repositorio
git clone [tu-repositorio]
cd gmb-scrape

# Instalar dependencias
pip install -r requirements.txt
```

## 🎯 Uso

### Modo Interactivo (Recomendado)
```bash
python main.py
```

El modo interactivo te guiará paso a paso:
1. Ingresa el término de búsqueda
2. Selecciona ubicaciones (departamento → provincia → distrito)
3. Configura filtros (rating, reviews, antigüedad)
4. Elige formato de salida (CSV/JSON)

### Modo CLI
```bash
# Búsqueda básica
python main.py "restaurantes" --departments Lima --min-rating 4.0

# Con múltiples filtros
python main.py "hoteles" \
    --departments Lima Cusco \
    --min-rating 4.5 \
    --min-reviews 100 \
    --min-age 365 \
    --format csv

# Modo headless (sin ventana del navegador)
python main.py "tiendas" --departments Arequipa --headless
```

### Con Archivo de Configuración
```bash
python main.py "restaurantes" --config config_example.json
```

## 📊 Salida de Datos

Los resultados se guardan con timestamp único:
- **CSV**: `gmb_[búsqueda]_[timestamp].csv`
- **JSON**: `gmb_[búsqueda]_[timestamp].json`

### Campos en la salida:
```json
{
  "name": "Nombre del Negocio",
  "rating": 4.5,
  "review_count": 234,
  "address": "Av. Example 123, Miraflores",
  "phone": "+51 1 234 5678",
  "website": "https://example.com",
  "email": "contacto@example.com",
  "emails": ["contacto@example.com", "ventas@example.com"],
  "category": "Restaurante",
  "hours": "Lunes a Viernes: 9:00-18:00",
  "age_days": 730,
  "department": "Lima",
  "province": "Lima",
  "district": "Miraflores",
  "location": "Miraflores, Lima, Lima",
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🗺️ Cobertura Geográfica

Base de datos completa de Perú:
- 24 Departamentos
- 196 Provincias
- 1,874 Distritos

## ⚙️ Configuración Avanzada

### Archivo de Configuración JSON
```json
{
  "locations": [
    ["Lima", "Lima", "Miraflores"],
    ["Cusco", "Cusco", "Cusco"]
  ],
  "filters": {
    "min_rating": 4.0,
    "min_reviews": 50,
    "min_age_days": 180,
    "max_age_days": 3650
  }
}
```

## 📈 Ejemplos de Uso

### Buscar restaurantes top en Lima
```bash
python main.py "restaurantes" \
    --departments Lima \
    --min-rating 4.5 \
    --min-reviews 100
```

### Extraer emails de hoteles en Cusco
```bash
python main.py "hoteles" \
    --departments Cusco \
    --format csv
```

### Análisis de competencia en múltiples ciudades
```bash
python main.py "agencias de viaje" \
    --departments Lima Cusco Arequipa \
    --min-rating 3.0 \
    --format both
```

## 🔧 Solución de Problemas

### Chrome/Chromium no encontrado
```bash
# Ubuntu/Debian
sudo apt-get install chromium-browser

# MacOS
brew install --cask chromium
```

### Timeout o errores de conexión
- Usa `--headless` para modo sin ventana
- Ajusta el tiempo de espera en el código
- Verifica tu conexión a internet

## 📝 Notas

- El scraper respeta los términos de servicio de Google
- Los emails extraídos son públicamente disponibles
- La velocidad depende de tu conexión y cantidad de resultados
- Se recomienda usar con moderación para evitar límites de rate

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea tu branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.