#!/usr/bin/env python3
"""
Script de prueba para diagnosticar problemas con el scraper
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_google_maps():
    print("🔍 Iniciando prueba de Google Maps...")
    
    # Configurar navegador
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # NO usar headless para esta prueba
    # options.add_argument('--headless')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Buscar hoteles en Lima
        query = "hoteles en Lima, Peru"
        url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        
        print(f"📍 Abriendo: {url}")
        driver.get(url)
        
        print("⏳ Esperando 10 segundos para que cargue...")
        time.sleep(10)
        
        # Buscar diferentes tipos de elementos
        print("\n🔎 Buscando elementos en la página...")
        
        # Método 1: Buscar por role="feed"
        try:
            feed = driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"]')
            print(f"✓ Encontrados {len(feed)} elementos con role='feed'")
        except:
            print("✗ No se encontraron elementos con role='feed'")
        
        # Método 2: Buscar enlaces a lugares
        try:
            places = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
            print(f"✓ Encontrados {len(places)} enlaces a lugares")
            if places:
                print(f"  Ejemplo: {places[0].text[:50]}...")
        except:
            print("✗ No se encontraron enlaces a lugares")
        
        # Método 3: Buscar por clases conocidas
        try:
            results = driver.find_elements(By.CSS_SELECTOR, 'div[class*="Nv2PK"]')
            print(f"✓ Encontrados {len(results)} elementos con clase Nv2PK")
        except:
            print("✗ No se encontraron elementos con clase Nv2PK")
        
        # Método 4: Buscar cualquier h3 (títulos de negocios)
        try:
            titles = driver.find_elements(By.TAG_NAME, 'h3')
            print(f"✓ Encontrados {len(titles)} títulos (h3)")
            if titles:
                print(f"  Primeros 3 títulos:")
                for i, title in enumerate(titles[:3]):
                    print(f"    {i+1}. {title.text}")
        except:
            print("✗ No se encontraron títulos")
        
        # Método 5: Buscar botones con aria-label
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label]')
            print(f"✓ Encontrados {len(buttons)} botones con aria-label")
        except:
            print("✗ No se encontraron botones")
        
        # Guardar screenshot para análisis
        driver.save_screenshot("test_google_maps.png")
        print("\n📸 Screenshot guardado como 'test_google_maps.png'")
        
        # Imprimir información de la página
        print(f"\n📄 Título de la página: {driver.title}")
        print(f"🔗 URL actual: {driver.current_url}")
        
        input("\n✋ Presiona Enter para cerrar el navegador...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        driver.quit()
        print("\n✅ Prueba completada")

if __name__ == "__main__":
    test_google_maps()