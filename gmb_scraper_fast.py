#!/usr/bin/env python3
"""
GMB Fast Scraper - Versión optimizada para extracción rápida
Extrae solo: Nombre, Teléfono y Website
Permite mayor volumen con menor riesgo de detección
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import random
import csv
from datetime import datetime
from tqdm import tqdm
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GMBFastScraper:
    def __init__(self, headless=False, max_results=30):
        self.driver = None
        self.headless = headless
        self.results = []
        self.max_results_per_location = max_results  # Aumentado a 30 por defecto
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
    def init_driver(self):
        """Inicializar driver con configuración optimizada"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        
        # Configuración básica anti-detección
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'--user-agent={random.choice(self.user_agents)}')
        
        # Ventana aleatoria
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f'--window-size={width},{height}')
        
        # Desactivar imágenes para mayor velocidad
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Ocultar webdriver
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 15)  # Reducido de 20 a 15
        logger.info("Driver initialized successfully")
        
    def quick_delay(self, min_seconds=0.5, max_seconds=2):
        """Delay más corto para extracción rápida"""
        time.sleep(random.uniform(min_seconds, max_seconds))
        
    def search_businesses(self, query, location):
        """Búsqueda optimizada de negocios"""
        try:
            search_query = f"{query} en {location}, Perú"
            url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            logger.info(f"Searching: {search_query}")
            self.driver.get(url)
            
            # Delay inicial más corto
            self.quick_delay(2, 3)
            
            # Aceptar cookies si aparecen
            try:
                accept_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Aceptar')]")
                accept_button.click()
                self.quick_delay(0.5, 1)
            except:
                pass
            
            # Esperar resultados
            self.quick_delay(1.5, 2.5)
            
            # Buscar elementos de negocio
            business_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
            
            if not business_elements:
                logger.warning("No businesses found")
                return []
            
            logger.info(f"Found {len(business_elements)} businesses")
            
            # Scroll mínimo para cargar más resultados
            if len(business_elements) < self.max_results_per_location:
                try:
                    results_container = self.driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
                    for _ in range(2):  # Solo 2 scrolls
                        self.driver.execute_script("arguments[0].scrollTop += 500", results_container)
                        self.quick_delay(0.8, 1.2)
                    
                    # Re-buscar elementos
                    business_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
                except:
                    pass
            
            # Limitar resultados
            business_elements = business_elements[:self.max_results_per_location]
            
            businesses = []
            for i, element in enumerate(business_elements):
                try:
                    logger.info(f"Extracting {i+1}/{len(business_elements)}")
                    
                    # Re-encontrar elementos (DOM cambia)
                    current_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
                    if i >= len(current_elements):
                        continue
                    
                    business_data = self.extract_basic_info(current_elements[i])
                    if business_data:
                        business_data['location'] = location
                        business_data['search_query'] = query
                        businesses.append(business_data)
                        
                    # Delay mínimo entre negocios
                    self.quick_delay(0.5, 1)
                    
                except Exception as e:
                    logger.debug(f"Error extracting business {i}: {e}")
                    continue
            
            return businesses
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return []
    
    def extract_basic_info(self, element):
        """Extracción minimalista: solo nombre, teléfono y web"""
        try:
            # Click en el elemento
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.3)
                element.click()
            except:
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                except:
                    return None
            
            # Espera mínima para carga - aumentada para asegurar carga completa
            self.quick_delay(2.5, 3.5)
            
            business_info = {
                'name': 'N/A',
                'phone': 'N/A',
                'website': 'N/A',
                'timestamp': datetime.now().isoformat()
            }
            
            # Verificar que estamos en la página de detalle (no en la lista)
            detail_opened = False
            
            # Método 1: Buscar botón de volver
            try:
                back_selectors = [
                    'button[aria-label*="Back"]',
                    'button[aria-label*="back"]', 
                    'button[aria-label*="Atrás"]',
                    'button[aria-label*="Volver"]',
                    'button[jsaction*="back"]',
                    'button.VfPpkd-icon-LgbsSe'  # Clase común del botón back
                ]
                for selector in back_selectors:
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, selector)
                        detail_opened = True
                        logger.debug(f"Found back button with selector: {selector}")
                        break
                    except:
                        continue
            except:
                pass
            
            # Método 2: Verificar si hay h1 con nombre (no "Resultados")
            if not detail_opened:
                try:
                    h1_elements = self.driver.find_elements(By.CSS_SELECTOR, 'h1')
                    for h1 in h1_elements:
                        text = h1.text.strip()
                        if text and text not in ['Resultados', 'Results', 'Search results', '']:
                            detail_opened = True
                            logger.debug(f"Found business name h1: {text[:30]}...")
                            break
                except:
                    pass
            
            # Método 3: Buscar información de teléfono/dirección que indica detalle
            if not detail_opened:
                try:
                    # Si encontramos botones de teléfono o sitio web, estamos en detalle
                    if self.driver.find_elements(By.CSS_SELECTOR, 'button[data-tooltip*="phone"], button[data-tooltip*="Phone"], a[data-tooltip*="website"], a[data-tooltip*="Website"]'):
                        detail_opened = True
                        logger.debug("Found phone/website buttons - detail page confirmed")
                except:
                    pass
            
            # Si aún no detectamos el detalle, intentar continuar de todos modos
            if not detail_opened:
                logger.warning("Could not confirm detail page, attempting extraction anyway")
                # No retornar None, intentar extraer de todos modos
            
            # 1. EXTRAER NOMBRE - Múltiples métodos mejorados
            # Método 1: Buscar en el aria-label del elemento clickeado (más confiable)
            try:
                aria_label = element.get_attribute('aria-label')
                if aria_label:
                    # El aria-label suele tener formato: "Nombre del negocio · Rating · Reviews"
                    name_from_aria = aria_label.split('·')[0].strip()
                    if name_from_aria and name_from_aria not in ['Resultados', 'Results']:
                        business_info['name'] = name_from_aria
            except:
                pass
            
            # Método 2: Buscar h1 pero con wait
            if business_info['name'] == 'N/A':
                try:
                    # Esperar a que aparezca un h1 válido
                    time.sleep(0.5)  # Pequeña espera adicional
                    h1_elements = self.driver.find_elements(By.CSS_SELECTOR, 'h1')
                    for h1 in h1_elements:
                        text = h1.text.strip()
                        if text and text not in ['Resultados', 'Results', 'Search results', '', 'Buscar en Google Maps']:
                            business_info['name'] = text
                            break
                except:
                    pass
            
            # Método 3: Buscar en divs con clases específicas de Google Maps
            if business_info['name'] == 'N/A':
                try:
                    # Múltiples selectores posibles para el nombre
                    name_selectors = [
                        'div[class*="fontHeadlineLarge"]',
                        'div[class*="DUwDvf"]',  # Clase común para títulos en GMaps
                        'div[role="heading"][aria-level="1"]',
                        'h1[class*="DUwDvf"]'
                    ]
                    for selector in name_selectors:
                        name_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in name_elements:
                            text = elem.text.strip()
                            if text and len(text) > 2 and text not in ['Resultados', 'Results', 'Buscar en Google Maps']:
                                business_info['name'] = text
                                break
                        if business_info['name'] != 'N/A':
                            break
                except:
                    pass
            
            # 2. EXTRAER TELÉFONO (búsqueda directa)
            try:
                # Buscar botones con data-tooltip que contenga "phone" o "teléfono"
                phone_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-tooltip*="phone"], button[data-tooltip*="Phone"], button[data-tooltip*="teléfono"], button[data-tooltip*="Teléfono"]')
                for btn in phone_buttons:
                    aria_label = btn.get_attribute('aria-label')
                    if aria_label and ('Phone:' in aria_label or 'Teléfono:' in aria_label):
                        phone = aria_label.split(':')[-1].strip()
                        if phone:
                            business_info['phone'] = phone
                            break
            except:
                pass
            
            # Fallback para teléfono: buscar en texto
            if business_info['phone'] == 'N/A':
                try:
                    # Buscar patterns de teléfono en el texto
                    all_text = self.driver.find_element(By.CSS_SELECTOR, 'div[role="main"]').text
                    import re
                    phone_pattern = r'(?:\+51\s?)?(?:\d{1,2}\s?)?\d{3}[\s-]?\d{3}[\s-]?\d{3,4}'
                    phones = re.findall(phone_pattern, all_text)
                    if phones:
                        business_info['phone'] = phones[0].strip()
                except:
                    pass
            
            # 3. EXTRAER WEBSITE (búsqueda rápida)
            try:
                # Buscar links con data-tooltip de website
                website_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[data-tooltip*="website"], a[data-tooltip*="Website"], a[data-tooltip*="sitio"], a[data-tooltip*="Sitio"]')
                for link in website_links:
                    href = link.get_attribute('href')
                    if href and not href.startswith('https://www.google.com'):
                        business_info['website'] = href
                        break
            except:
                pass
            
            # Volver a la lista (sin verificar, más rápido)
            try:
                back_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Back"], button[aria-label*="back"], button[aria-label*="Atrás"]')
                back_button.click()
                self.quick_delay(0.8, 1.2)
            except:
                # Si no hay botón, intentar navegador back
                self.driver.back()
                self.quick_delay(1, 1.5)
            
            # Log resultado extraído
            logger.info(f"Extracted: {business_info['name'][:30] if business_info['name'] != 'N/A' else 'N/A'} | Phone: {business_info['phone'] != 'N/A'} | Web: {business_info['website'] != 'N/A'}")
            
            return business_info
            
        except Exception as e:
            logger.debug(f"Error extracting info: {e}")
            # Intentar volver a la lista
            try:
                self.driver.back()
            except:
                pass
            return None
    
    def save_results(self, format='csv'):
        """Guardar resultados en archivo"""
        if not self.results:
            logger.warning("No results to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'csv' or format == 'both':
            filename = f"gmb_fast_{timestamp}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'phone', 'website', 'location', 'search_query', 'timestamp'])
                writer.writeheader()
                writer.writerows(self.results)
            logger.info(f"Results saved to {filename}")
        
        if format == 'json' or format == 'both':
            filename = f"gmb_fast_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            logger.info(f"Results saved to {filename}")
        
        # Mostrar resumen
        print(f"\n{'='*50}")
        print(f"EXTRACTION COMPLETE")
        print(f"{'='*50}")
        print(f"Total businesses extracted: {len(self.results)}")
        print(f"Businesses with phone: {sum(1 for r in self.results if r['phone'] != 'N/A')}")
        print(f"Businesses with website: {sum(1 for r in self.results if r['website'] != 'N/A')}")
    
    def run(self, query, locations, format='csv'):
        """Ejecutar scraping completo"""
        self.init_driver()
        
        try:
            for location in tqdm(locations, desc="Processing locations"):
                logger.info(f"Processing: {location}")
                businesses = self.search_businesses(query, location)
                self.results.extend(businesses)
                
                # Delay entre ubicaciones (reducido)
                if location != locations[-1]:
                    self.quick_delay(2, 3)
            
            self.save_results(format)
            
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Driver closed")

def main():
    parser = argparse.ArgumentParser(description='GMB Fast Scraper - Extract name, phone and website only')
    parser.add_argument('query', help='Search query (e.g., "restaurants", "hotels")')
    parser.add_argument('--locations', nargs='+', default=['Lima'], help='Locations to search')
    parser.add_argument('--max-results', type=int, default=30, help='Max results per location (default: 30)')
    parser.add_argument('--format', choices=['csv', 'json', 'both'], default='csv', help='Output format')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    args = parser.parse_args()
    
    print("""
    ╔════════════════════════════════════════╗
    ║      GMB FAST SCRAPER - PERU 🚀       ║
    ║   Extract: Name, Phone, Website Only   ║
    ╚════════════════════════════════════════╝
    """)
    
    scraper = GMBFastScraper(
        headless=args.headless,
        max_results=args.max_results
    )
    
    scraper.run(
        query=args.query,
        locations=args.locations,
        format=args.format
    )

if __name__ == "__main__":
    main()