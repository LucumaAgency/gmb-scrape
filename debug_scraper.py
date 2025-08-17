#!/usr/bin/env python3
"""
Script de diagnóstico detallado para el scraper
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

# Configurar logging detallado
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_google_maps():
    print("🔍 Debug detallado del scraper...")
    
    # Configurar navegador
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Buscar agencias de marketing en Lima
        query = "agencia de marketing en Lima, Peru"
        url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        
        print(f"📍 Abriendo: {url}")
        driver.get(url)
        
        print("⏳ Esperando que cargue la página...")
        time.sleep(5)
        
        # Buscar elementos de negocios
        print("\n🔎 Buscando negocios...")
        business_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
        print(f"✓ Encontrados {len(business_elements)} negocios")
        
        if len(business_elements) > 0:
            print(f"\n📋 Intentando hacer clic en el primer negocio...")
            
            # Obtener información del primer elemento antes de hacer clic
            first_element = business_elements[0]
            aria_label = first_element.get_attribute('aria-label')
            href = first_element.get_attribute('href')
            
            print(f"  - aria-label: {aria_label}")
            print(f"  - href: {href[:100]}...")
            
            # Hacer clic
            print("\n👆 Haciendo clic...")
            first_element.click()
            
            # Esperar un momento
            time.sleep(3)
            
            print("\n🔍 Analizando qué pasó después del clic...")
            
            # Buscar indicadores de que se abrió la vista de detalles
            detail_indicators = {
                'back_button': False,
                'h1_title': False,
                'rating': False,
                'address': False,
                'phone': False
            }
            
            # 1. Buscar botón de volver
            try:
                back_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="Back"], button[aria-label*="Atrás"], button[aria-label*="Volver"]')
                if back_buttons:
                    detail_indicators['back_button'] = True
                    print(f"✓ Botón de volver encontrado: {back_buttons[0].get_attribute('aria-label')}")
            except:
                print("✗ No se encontró botón de volver")
            
            # 2. Buscar título h1
            try:
                h1_elements = driver.find_elements(By.TAG_NAME, 'h1')
                for h1 in h1_elements:
                    if h1.text and h1.text != "Resultados":
                        detail_indicators['h1_title'] = True
                        print(f"✓ Título h1 encontrado: '{h1.text}'")
                        print(f"  - Clases del h1: {h1.get_attribute('class')}")
                        break
                if not detail_indicators['h1_title']:
                    print("✗ No se encontró un h1 válido con nombre de negocio")
            except:
                print("✗ Error buscando h1")
            
            # 3. Buscar rating
            try:
                rating_elements = driver.find_elements(By.CSS_SELECTOR, 'span[aria-label*="star"], span[aria-label*="estrella"]')
                if rating_elements:
                    detail_indicators['rating'] = True
                    print(f"✓ Rating encontrado: {rating_elements[0].get_attribute('aria-label')}")
            except:
                print("✗ No se encontró rating")
            
            # 4. Buscar dirección
            try:
                address_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-item-id*="address"]')
                if address_buttons:
                    detail_indicators['address'] = True
                    print(f"✓ Dirección encontrada: {address_buttons[0].get_attribute('aria-label')}")
            except:
                print("✗ No se encontró dirección")
            
            # 5. Buscar teléfono
            try:
                phone_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-item-id*="phone"]')
                if phone_buttons:
                    detail_indicators['phone'] = True
                    print(f"✓ Teléfono encontrado: {phone_buttons[0].get_attribute('aria-label')}")
            except:
                print("✗ No se encontró teléfono")
            
            # Resumen
            print("\n📊 RESUMEN:")
            opened_count = sum(detail_indicators.values())
            if opened_count >= 3:
                print("✅ La vista de detalles SÍ se abrió correctamente")
            else:
                print("❌ La vista de detalles NO se abrió correctamente")
            
            print(f"\nIndicadores encontrados: {opened_count}/5")
            for key, value in detail_indicators.items():
                status = "✓" if value else "✗"
                print(f"  {status} {key}")
            
            # Buscar todos los elementos con texto para debug
            print("\n📄 Elementos con texto en la página:")
            text_elements = driver.find_elements(By.XPATH, '//*[text()]')
            unique_texts = set()
            for elem in text_elements[:30]:  # Solo los primeros 30
                text = elem.text.strip()
                if text and len(text) > 3 and len(text) < 100:
                    unique_texts.add(text)
            
            for i, text in enumerate(list(unique_texts)[:15], 1):
                print(f"  {i}. {text[:60]}...")
            
            # Intentar volver a la lista
            if detail_indicators['back_button']:
                print("\n🔙 Intentando volver a la lista...")
                back_buttons[0].click()
                time.sleep(2)
                
                # Verificar si volvimos
                new_business_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
                if len(new_business_elements) > 1:
                    print(f"✓ Volvimos a la lista. Ahora hay {len(new_business_elements)} negocios")
                else:
                    print("✗ No parece que hayamos vuelto a la lista")
        
        # Guardar screenshot
        driver.save_screenshot("debug_scraper.png")
        print("\n📸 Screenshot guardado como 'debug_scraper.png'")
        
        input("\n✋ Presiona Enter para cerrar el navegador...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("\n✅ Debug completado")

if __name__ == "__main__":
    debug_google_maps()