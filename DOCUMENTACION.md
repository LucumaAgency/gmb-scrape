# gmb-scrape — cómo se usa y en qué estado está

Scraper de fichas de Google Maps (GMB) para Perú, que alimenta la cola comercial de Lucuma.
Estado al 19-08-2026.

## El flujo completo, de Google a la cola de trabajo

```
correr_campana.py  ->  campana.json/.csv  ->  a_csv_comercial.py  ->  gmb/prospectos-gmb-peru.csv
                                                                              |
                                                                     comercial/generar-cola.py
                                                                              |
                                                                     COLA.md, sección 8
```

### 1. Scrapear

```bash
python3 correr_campana.py \
    --rubros "inmobiliaria,agente inmobiliario,bienes raices" \
    --distritos "Surco,San Borja" \
    --por-busqueda 25 --tope 100
```

- `--por-busqueda`: fichas por combinación rubro-distrito.
- `--tope`: tope duro de la sesión. **Recomendado 300-500/día por IP.**
- `--pausa "20,40"`: segundos entre búsquedas. Bajarlo solo para pruebas cortas.
- `--estado`: ver el progreso acumulado sin scrapear nada.

### 2. Convertir a prospectos

```bash
python3 a_csv_comercial.py campana_gmb.json \
    --salida ../gmb/prospectos-gmb-peru.csv --servicio SEO --solo-con-contacto
```

Es **idempotente**: conserva las filas que ya estaban (Estado, Fecha contacto, Notas: el trabajo
comercial hecho) y solo agrega negocios nuevos.

### 3. Regenerar la cola

```bash
python3 comercial/generar-cola.py
```

---

## Cómo sabemos que no repetimos negocios entre corridas

Hay **tres redes**, de la más importante a la última:

### 1. `vistos.jsonl` — el historial permanente (automático)

Cada negocio extraído queda anotado con su `place_id` y con `nombre|dirección`. El historial se
carga **solo**, en cada corrida, sin pasar ningún flag: si un negocio ya está ahí, no se vuelve a
abrir. Esto es lo que hace que scrapear Pueblo Libre otro día no repita lo de hoy.

Comprobado el 19-08-2026: con 314 negocios en el historial, se relanzó Pueblo Libre sin ningún
flag y devolvió **13 fichas, cero solapamiento** con las anteriores.

Ver qué hay dentro:

```bash
wc -l vistos.jsonl                      # cuántos negocios conocemos
grep -c "Pueblo Libre" vistos.jsonl     # cuántos de un distrito
```

Para re-scrapear algo a propósito (por ejemplo, refrescar datos viejos): `--sin-historial`.

Si el historial se pierde, se reconstruye desde los JSON de las corridas:

```bash
python3 sembrar_vistos.py *.json
```

### 2. `progreso.jsonl` — qué combinaciones rubro×distrito ya se hicieron

Evita repetir la **búsqueda** entera. Una combinación cortada por el tope queda `parcial` y se
reintenta completa la próxima vez. Sobrevive a cortes (escribe con `fsync`).

### 3. Dedup dentro de la corrida y al volcar al CSV

- En la corrida: `place_id` sacado del href, más una segunda red por nombre+dirección.
- Al volcar: `a_csv_comercial.py` deduplica por teléfono, luego dominio, luego nombre.

---

## Qué se scrapeó hasta ahora (19-08-2026)

| Distrito | Fichas | Notas |
|---|---|---|
| San Isidro | 103 | "inmobiliaria" **agotado** (~51 negocios); el resto salió de términos alternativos |
| Miraflores | 97 | 3 de 6 términos se agotaron antes del cupo |
| Pueblo Libre | 81 | 78/100 estaban realmente en el distrito (ver limitaciones) |

Total: **327 negocios únicos** en el historial, **281 prospectos** en la cola comercial
(126 con email).

Rendimiento medido: **~11 s por ficha** (~330/hora). 100 fichas ≈ 19 minutos.

El email es el campo que más varía por zona: 60% en San Isidro, 43% en Miraflores, 27% en
Pueblo Libre. A negocio más chico, menos correo publicado.

---

## Limitaciones conocidas

- **Un término se agota.** Google devuelve ~50 resultados por búsqueda. Para sacar más de un
  distrito hay que variar el término (agente inmobiliario, bienes raíces, corredor, consultora...),
  no repetir el mismo.
- **La columna `Ciudad` es el distrito buscado, no el real.** Cuando un distrito chico se agota,
  Maps ensancha el radio: en Pueblo Libre, 22 de 100 fichas eran de distritos vecinos.
- **Bloqueos.** El scraper detecta captcha / muro de consentimiento / página vacía y **aborta**
  la corrida con captura de pantalla, en vez de seguir devolviendo ceros en silencio. Si pasa:
  esperar unas horas o cambiar de IP. Lo ya guardado sigue siendo válido y el progreso permite
  retomar.
- **Las tres GUIs** (`gui.py`, `gui_fixed.py`, `gui_debug.py`) siguen siendo variantes de lo mismo
  y no recibieron ninguno de los arreglos recientes. El camino probado es la línea de comandos.
- Los `test_*.py` no son una suite: son scripts de depuración manuales.

## Verificación rápida de que el scraper sigue vivo

```bash
python3 smoke_test.py "estudio contable" "San Isidro"
```

Reporta la cobertura campo por campo. Si `name` o `address` salen 0/3, Google cambió el DOM y hay
que revisar los selectores. Ver `PRUEBA-DE-HUMO.md` para el diagnóstico y los arreglos históricos.
