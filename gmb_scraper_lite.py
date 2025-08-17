from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re
from datetime import datetime, timedelta
from dateutil import parser
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    import csv
from tqdm import tqdm
import logging
import requests
from bs4 import BeautifulSoup
import urllib3

# Suppress SSL warnings for website scraping
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GMBScraper:
    def __init__(self, headless=False):
        self.driver = None
        self.headless = headless
        self.results = []
        
    def init_driver(self):
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use webdriver-manager to automatically download the correct driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 20)
        
    def search_business(self, query, location):
        try:
            search_query = f"{query} en {location}, Perú"
            url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            self.driver.get(url)
            time.sleep(3)
            
            results_container = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]'))
            )
            
            last_height = 0
            scroll_attempts = 0
            max_scrolls = 10
            
            while scroll_attempts < max_scrolls:
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_container)
                time.sleep(2)
                
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", results_container)
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_attempts += 1
            
            business_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] > div > div[jsaction]')
            
            businesses = []
            for i, element in enumerate(business_elements):
                try:
                    # Re-find elements to avoid stale references
                    current_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] > div > div[jsaction]')
                    if i < len(current_elements):
                        business_data = self.extract_business_info(current_elements[i], location)
                        if business_data:
                            businesses.append(business_data)
                except Exception as e:
                    logger.debug(f"Error extracting business {i}: {e}")
                    continue
                    
            return businesses
            
        except Exception as e:
            logger.error(f"Error searching businesses: {e}")
            return []
    
    def extract_business_info(self, element, location):
        try:
            # Re-find element to avoid stale reference
            try:
                element.click()
            except:
                # If element is stale, try to find it again
                time.sleep(1)
                return None
            
            time.sleep(2)
            
            business_info = {
                'location': location,
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                name_element = self.driver.find_element(By.CSS_SELECTOR, 'h1[class*="fontHeadlineLarge"]')
                business_info['name'] = name_element.text
            except:
                business_info['name'] = 'N/A'
            
            try:
                rating_element = self.driver.find_element(By.CSS_SELECTOR, 'div[jsaction*="pane.rating.starColor"] span[aria-hidden="true"]')
                business_info['rating'] = float(rating_element.text.replace(',', '.'))
            except:
                business_info['rating'] = 0.0
            
            try:
                reviews_element = self.driver.find_element(By.CSS_SELECTOR, 'button[jsaction*="pane.rating.moreReviews"] span')
                reviews_text = reviews_element.text
                reviews_match = re.search(r'\((\d+\.?\d*[KkMm]?)\)', reviews_text)
                if reviews_match:
                    reviews_str = reviews_match.group(1)
                    if 'K' in reviews_str.upper():
                        business_info['review_count'] = int(float(reviews_str.replace('K', '').replace('k', '')) * 1000)
                    elif 'M' in reviews_str.upper():
                        business_info['review_count'] = int(float(reviews_str.replace('M', '').replace('m', '')) * 1000000)
                    else:
                        business_info['review_count'] = int(reviews_str)
                else:
                    business_info['review_count'] = 0
            except:
                business_info['review_count'] = 0
            
            try:
                address_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]')
                business_info['address'] = address_button.get_attribute('aria-label').replace('Dirección: ', '')
            except:
                business_info['address'] = 'N/A'
            
            try:
                phone_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id*="phone"]')
                business_info['phone'] = phone_button.get_attribute('aria-label').replace('Teléfono: ', '')
            except:
                business_info['phone'] = 'N/A'
            
            try:
                website_button = self.driver.find_element(By.CSS_SELECTOR, 'a[data-item-id="authority"]')
                business_info['website'] = website_button.get_attribute('href')
            except:
                business_info['website'] = 'N/A'
            
            try:
                category_element = self.driver.find_element(By.CSS_SELECTOR, 'button[jsaction*="pane.rating.category"]')
                business_info['category'] = category_element.text
            except:
                business_info['category'] = 'N/A'
            
            try:
                hours_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id*="hours"]')
                business_info['hours'] = hours_button.get_attribute('aria-label')
            except:
                business_info['hours'] = 'N/A'
            
            # Extraer emails
            emails = self.extract_emails_from_gmb()
            
            # Si hay website, intentar extraer emails del sitio web también
            if business_info['website'] != 'N/A':
                website_emails = self.extract_emails_from_website(business_info['website'])
                emails.extend(website_emails)
            
            # Eliminar duplicados y validar emails
            emails = list(set([email for email in emails if self.validate_email(email)]))
            business_info['emails'] = emails if emails else []
            business_info['email'] = emails[0] if emails else 'N/A'
            
            business_info['age_days'] = self.estimate_business_age()
            
            return business_info
            
        except Exception as e:
            logger.error(f"Error extracting business info: {e}")
            return None
    
    def validate_email(self, email):
        """Valida si un string es un email válido"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email.lower()) is not None
    
    def extract_emails_from_gmb(self):
        """Extrae emails desde la página de GMB"""
        emails = []
        try:
            # Buscar en toda la información visible de GMB
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            
            # Buscar patrones de email en el texto
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            found_emails = re.findall(email_pattern, page_text)
            emails.extend(found_emails)
            
            # Buscar en elementos específicos que podrían contener emails
            try:
                # Buscar en la sección de información
                info_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="rogA2c"] a[href^="mailto:"]')
                for elem in info_elements:
                    email = elem.get_attribute('href').replace('mailto:', '')
                    if email:
                        emails.append(email)
            except:
                pass
            
            # Buscar en descripciones y otros textos
            try:
                description_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="WeS02d"]')
                for elem in description_elements:
                    text = elem.text
                    found_emails = re.findall(email_pattern, text)
                    emails.extend(found_emails)
            except:
                pass
                
        except Exception as e:
            logger.debug(f"Error extracting emails from GMB: {e}")
        
        return emails
    
    def extract_emails_from_website(self, url, timeout=10):
        """Extrae emails desde el sitio web del negocio"""
        emails = []
        
        if not url or url == 'N/A':
            return emails
            
        try:
            # Hacer request al sitio web
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout, verify=False)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Buscar emails en el HTML
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                
                # Buscar en todo el texto
                page_text = soup.get_text()
                found_emails = re.findall(email_pattern, page_text)
                emails.extend(found_emails)
                
                # Buscar en enlaces mailto
                mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
                for link in mailto_links:
                    email = link.get('href').replace('mailto:', '').split('?')[0]
                    if email:
                        emails.append(email)
                
                # Buscar en meta tags
                meta_tags = soup.find_all('meta')
                for tag in meta_tags:
                    content = tag.get('content', '')
                    found_emails = re.findall(email_pattern, content)
                    emails.extend(found_emails)
                
                # Buscar páginas de contacto
                contact_links = []
                for link in soup.find_all('a', href=True):
                    href = link['href'].lower()
                    if any(word in href for word in ['contact', 'contacto', 'contactenos', 'contact-us']):
                        contact_links.append(link['href'])
                
                # Visitar primera página de contacto encontrada
                if contact_links and len(emails) == 0:
                    contact_url = contact_links[0]
                    if not contact_url.startswith('http'):
                        from urllib.parse import urljoin
                        contact_url = urljoin(url, contact_url)
                    
                    try:
                        contact_response = requests.get(contact_url, headers=headers, timeout=5, verify=False)
                        if contact_response.status_code == 200:
                            contact_soup = BeautifulSoup(contact_response.text, 'html.parser')
                            contact_text = contact_soup.get_text()
                            found_emails = re.findall(email_pattern, contact_text)
                            emails.extend(found_emails)
                    except:
                        pass
                
        except Exception as e:
            logger.debug(f"Error extracting emails from website {url}: {e}")
        
        # Filtrar emails genéricos y no válidos
        filtered_emails = []
        generic_domains = ['example.com', 'email.com', 'test.com', 'domain.com', 'yoursite.com', 'website.com']
        
        for email in emails:
            email_lower = email.lower()
            if not any(domain in email_lower for domain in generic_domains):
                if '@' in email and '.' in email.split('@')[1]:
                    filtered_emails.append(email)
        
        return filtered_emails
    
    def estimate_business_age(self):
        try:
            reviews_button = self.driver.find_element(By.CSS_SELECTOR, 'button[jsaction*="pane.rating.moreReviews"]')
            reviews_button.click()
            time.sleep(2)
            
            review_dates = self.driver.find_elements(By.CSS_SELECTOR, 'span[class*="rsqaWe"]')
            
            oldest_date = datetime.now()
            for date_element in review_dates[:20]:
                try:
                    date_text = date_element.text
                    if 'hace' in date_text:
                        if 'año' in date_text:
                            years = int(re.search(r'(\d+)', date_text).group(1))
                            review_date = datetime.now() - timedelta(days=years*365)
                        elif 'mes' in date_text:
                            months = int(re.search(r'(\d+)', date_text).group(1))
                            review_date = datetime.now() - timedelta(days=months*30)
                        elif 'semana' in date_text:
                            weeks = int(re.search(r'(\d+)', date_text).group(1))
                            review_date = datetime.now() - timedelta(weeks=weeks)
                        elif 'día' in date_text:
                            days = int(re.search(r'(\d+)', date_text).group(1))
                            review_date = datetime.now() - timedelta(days=days)
                        else:
                            continue
                        
                        if review_date < oldest_date:
                            oldest_date = review_date
                except:
                    continue
            
            age_days = (datetime.now() - oldest_date).days
            
            back_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Atrás"]')
            back_button.click()
            time.sleep(1)
            
            return age_days
            
        except:
            return 0
    
    def filter_results(self, businesses, min_rating=0, min_reviews=0, min_age_days=0, max_age_days=36500):
        filtered = []
        for business in businesses:
            if (business.get('rating', 0) >= min_rating and
                business.get('review_count', 0) >= min_reviews and
                min_age_days <= business.get('age_days', 0) <= max_age_days):
                filtered.append(business)
        return filtered
    
    def search_location(self, query, department, province, district, **filters):
        location = f"{district}, {province}, {department}"
        logger.info(f"Searching: {query} in {location}")
        
        businesses = self.search_business(query, location)
        filtered_businesses = self.filter_results(businesses, **filters)
        
        for business in filtered_businesses:
            business['department'] = department
            business['province'] = province
            business['district'] = district
            
        self.results.extend(filtered_businesses)
        return filtered_businesses
    
    def save_results(self, filename='gmb_results', format='both'):
        if format in ['csv', 'both']:
            if PANDAS_AVAILABLE:
                df = pd.DataFrame(self.results)
                df.to_csv(f'{filename}.csv', index=False, encoding='utf-8-sig')
            else:
                # Fallback to csv module if pandas is not available
                if self.results:
                    keys = self.results[0].keys()
                    with open(f'{filename}.csv', 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.DictWriter(f, fieldnames=keys)
                        writer.writeheader()
                        writer.writerows(self.results)
            logger.info(f"Results saved to {filename}.csv")
            
        if format in ['json', 'both']:
            with open(f'{filename}.json', 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            logger.info(f"Results saved to {filename}.json")
    
    def close(self):
        if self.driver:
            self.driver.quit()