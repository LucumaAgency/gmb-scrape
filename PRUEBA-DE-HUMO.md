# Prueba de humo — gmb-scrape

Fecha: 2026-08-16 · Repo: LucumaAgency/gmb-scrape v1.1.4 (último commit ene-2025)
Entorno: Chrome 141, Python 3.10, headless. Comando: `python3 smoke_test.py restaurantes Miraflores`

## Veredicto

**El scraper sigue funcionando.** 3/3 fichas abiertas y extraídas en Miraflores. Los selectores
del panel de detalle (`data-item-id="address"`, `phone`, `authority`) siguen vigentes 19 meses después.
Pero hay 3 defectos reales que hacen que los datos NO sean confiables tal cual salen.

## Salud de campos (3 resultados)

| Campo | Estado | Nota |
|---|---|---|
| name | OK 3/3 | |
| rating | **DUDOSO** 3/3 | valores repetidos entre negocios distintos |
| review_count | **DUDOSO** 3/3 | idem |
| address | OK 3/3 | |
| phone | OK 2/3 | el negocio sin teléfono no lo publica, no es bug |
| website | OK 2/3 | idem |
| category | OK 3/3 | |
| hours | ROTO 0/3 | |
| emails | ROTO 0/3 | |

## Defectos confirmados

### 1. rating y review_count se leen de toda la página, no de la ficha abierta
`gmb_scraper_lite.py:367,378,395,409` usan `self.driver.find_elements(...)` global en vez de buscar
dentro del panel de detalle. Toman la primera coincidencia del DOM, que es la del **listado**, no la
del negocio abierto. Evidencia: "Eden Bar Lima" y "República del Pisco" salieron ambos con
rating 4.9 y exactamente 4700 reviews.

Impacto: el filtro `min_rating` / `min_reviews` — la razón de ser del scraper — filtra sobre datos
equivocados.

### 2. Horarios: selector en inglés sobre una página en español
`gmb_scraper_lite.py:451` busca `div[aria-label*="hours"]`. Maps en Perú renderiza "horario".
Siempre cae al `except` y escribe 'N/A'.

### 3. Emails: se saltan la mitad de las webs, y solo miran la home
- `gmb_scraper_lite.py:460`: `if ... and random.random() > 0.5` — solo visita la web del negocio
  **el 50% de las veces**, a propósito, "para evitar detección". La mitad de los leads pierde su email
  sin que nada lo indique.
- `extract_emails_from_website` hace un solo GET a la URL dada. El README promete rastrear "páginas de
  contacto"; eso no existe en el código.
- Verificado aparte: las 2 webs de la muestra tampoco tienen email en el HTML de la home (son páginas
  de reservas JS). El rendimiento real de este campo en rubros gastronómicos va a ser bajo aunque se
  arregle.

## Arreglos aplicados (2026-08-16, sobre gmb_scraper_lite.py)

1. **Panel de detalle aislado.** Nuevo `get_detail_panel()`: Maps renderiza dos `div[role="main"]`
   (listado y ficha); ahora rating, reviews, dirección, teléfono, web, categoría, horarios y emails
   se buscan **dentro de la ficha**. `rating`/`review_count` se leen de `div.F7nice` ("4.9" + "(1,599)")
   con fallback por `aria-label` en español e inglés. Los selectores `span.MW4etd` / `span.UY7F9`
   que usaba el código ya no existen en la ficha: eran del listado.
2. **Horarios.** Nuevo `extract_hours()`: lee el `aria-label` del bloque de horarios (semana completa),
   con fallback al estado actual visible; limpia los glifos de iconos y el sufijo "Copiar el horario".
3. **Emails.** Se eliminó el `random.random() > 0.5` que saltaba la mitad de las webs. Se añadió
   `_find_contact_urls()`: si la home no da email, sigue hasta 2 enlaces de contacto del mismo dominio.
   Se descartan `script`/`style` antes de aplicar el regex y se filtra ruido (dominios de plataformas
   tipo wixpress/sentry/googleapis, buzones `noreply`, y falsos positivos tipo `logo@2x.png`).

### Verificación posterior

`python3 smoke_test.py "estudio contable" "San Isidro"` → **9/9 campos OK**, incluidos
`hours` 3/3 y `emails` 3/3 (`info@laney.com.pe`, `info@symcontadores.com`).

`python3 smoke_test.py restaurantes Miraflores` → ratings ahora distintos y correctos por negocio
(Paco Yonque 4.9 / 1599, contrastado contra el DOM real; antes salía 4.9 / 4700 repetido).

## Duplicados y patrocinados (resuelto)

Los duplicados no venían de "volver al listado" sino de que **Maps reordena el listado después de
cada clic**: unas tarjetas se abrían dos veces y otras no se visitaban nunca. Por eso pedir 10
devolvía 6-9.

Ahora `search_business` no hace clic en el listado:

1. `recolectar_candidatos()` recorre el listado una sola vez (scrolleando hasta juntar de más),
   descarta anuncios y saca `(place_id, href, nombre)` de cada tarjeta.
2. Cada ficha se abre navegando a su URL (`extraer_desde_url`), no clicando.
3. `self.vistos` guarda los `place_id` de la sesión; queda una segunda red por nombre+dirección
   para las fichas sin `place_id` legible.

El `place_id` sale del token `!1s` del href y se guarda en cada resultado.

**Resultado medido** (inmobiliaria, San Isidro, `--por-busqueda 10`): 10 fichas, 10 nombres únicos,
10 place_id únicos, y el ritmo bajó de **13 a 9 s por ficha** (~400/hora) porque desaparecieron los
clics fallidos y las vueltas atrás.

## Lo que la prueba NO cubrió

- `gmb_scraper.py` (undetected-chromedriver) y `gmb_scraper_fast.py`: no probados.
- Las 3 GUIs: no probadas.
- Volumen / captcha: 1 búsqueda no dice nada sobre qué pasa a los 200 distritos.
- `estimate_business_age` (solo existe en `gmb_scraper.py`): no probado, pero devuelve 0 ante
  cualquier fallo, y 0 pasa cualquier filtro de antigüedad.

## Dependencia faltante

`tqdm` está en requirements.txt pero no estaba instalado; `gmb_scraper_lite.py` lo importa a nivel de
módulo y revienta el import. Instalado durante la prueba.
