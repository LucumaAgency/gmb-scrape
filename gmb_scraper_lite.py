from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re
import random
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
        self.max_results_per_location = 10  # Limit to 10 results
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        ]
        
    def init_driver(self):
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Random user agent
        user_agent = random.choice(self.user_agents)
        options.add_argument(f'--user-agent={user_agent}')
        logger.info(f"Using User-Agent: {user_agent[:50]}...")
        
        # Random window size
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f'--window-size={width},{height}')
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Additional anti-detection
        options.add_argument('--disable-features=AutomationControlled')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Execute script to remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 20)
        self.actions = ActionChains(self.driver)
        
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Random delay to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        
    def random_mouse_movement(self):
        """Simulate random mouse movements"""
        try:
            # Move mouse to random position
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            self.actions.move_by_offset(x, y).perform()
            self.random_delay(0.1, 0.3)
            # Reset mouse position
            self.actions.move_by_offset(-x, -y).perform()
        except:
            pass
            
    def human_scroll(self, element):
        """Scroll like a human - gradually"""
        try:
            scroll_pause = random.uniform(0.5, 1.5)
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", element)
            
            scroll_count = 0
            max_scrolls = 3  # Limit scrolls to avoid detection
            
            while scroll_count < max_scrolls:
                # Scroll a random amount
                scroll_amount = random.randint(300, 700)
                self.driver.execute_script(f"arguments[0].scrollTop += {scroll_amount}", element)
                
                self.random_delay(scroll_pause, scroll_pause + 1)
                
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", element)
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_count += 1
                
                # Random mouse movement during scroll
                if random.random() > 0.5:
                    self.random_mouse_movement()
                    
        except Exception as e:
            logger.debug(f"Error during scroll: {e}")
        
    def search_business(self, query, location):
        try:
            search_query = f"{query} en {location}, Perú"
            url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            logger.info(f"Loading URL: {url}")
            self.driver.get(url)
            
            # Random delay after page load
            self.random_delay(3, 6)
            
            # Random mouse movement
            self.random_mouse_movement()
            
            # Check if we need to accept cookies
            try:
                accept_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Aceptar')]")
                self.random_delay(0.5, 1)
                accept_button.click()
                self.random_delay(1, 2)
            except:
                pass
            
            # Wait for results with random delay
            self.random_delay(2, 4)
            
            # Find business elements using the selectors that work
            business_elements = []
            
            # Primary selector - links to places
            try:
                business_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
                if business_elements:
                    logger.info(f"Found {len(business_elements)} businesses using place links")
            except:
                pass
            
            # Fallback to Nv2PK class
            if not business_elements:
                try:
                    business_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="Nv2PK"]')
                    if business_elements:
                        logger.info(f"Found {len(business_elements)} businesses using Nv2PK class")
                except:
                    pass
            
            if not business_elements:
                logger.warning("No business elements found")
                return []
            
            # Scroll to load more results (but not too much)
            try:
                results_container = self.driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
                self.human_scroll(results_container)
            except:
                pass
            
            # Re-find elements after scroll
            try:
                business_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
            except:
                pass
            
            # Limit results to max_results_per_location
            business_elements = business_elements[:self.max_results_per_location]
            logger.info(f"Processing {len(business_elements)} businesses (max: {self.max_results_per_location})")
            
            businesses = []
            for i, element in enumerate(business_elements):
                if i >= self.max_results_per_location:
                    break
                    
                try:
                    # Random delay between businesses
                    self.random_delay(1, 3)
                    
                    # Random mouse movement
                    if random.random() > 0.7:
                        self.random_mouse_movement()
                    
                    business_data = self.extract_business_info(element, location)
                    if business_data:
                        businesses.append(business_data)
                        logger.info(f"Extracted business {i+1}/{len(business_elements)}: {business_data.get('name', 'Unknown')}")
                except Exception as e:
                    logger.debug(f"Error extracting business {i}: {e}")
                    continue
                    
            return businesses
            
        except Exception as e:
            logger.error(f"Error searching businesses: {e}")
            return []
    
    def extract_business_info(self, element, location):
        try:
            # Try to click with random delay
            try:
                self.random_delay(0.5, 1.5)
                element.click()
            except:
                # If element is stale or can't click, skip
                return None
            
            # Wait for information to load
            self.random_delay(2, 3)
            
            business_info = {
                'location': location,
                'timestamp': datetime.now().isoformat()
            }
            
            # Extract name - try multiple selectors
            try:
                name_element = self.driver.find_element(By.CSS_SELECTOR, 'h1[class*="fontHeadlineLarge"]')
                business_info['name'] = name_element.text
            except:
                try:
                    name_element = self.driver.find_element(By.CSS_SELECTOR, 'h1')
                    business_info['name'] = name_element.text
                except:
                    business_info['name'] = 'N/A'
            
            # Extract rating
            try:
                rating_element = self.driver.find_element(By.CSS_SELECTOR, 'span[role="img"][aria-label*="stars"]')
                rating_text = rating_element.get_attribute('aria-label')
                rating_match = re.search(r'([\d.]+)\s*stars?', rating_text)
                if rating_match:
                    business_info['rating'] = float(rating_match.group(1))
                else:
                    business_info['rating'] = 0.0
            except:
                business_info['rating'] = 0.0
            
            # Extract review count
            try:
                reviews_element = self.driver.find_element(By.CSS_SELECTOR, 'button[jsaction*="reviews"] span')
                reviews_text = reviews_element.text
                reviews_match = re.search(r'\(?([\d,]+)\)?', reviews_text)
                if reviews_match:
                    business_info['review_count'] = int(reviews_match.group(1).replace(',', ''))
                else:
                    business_info['review_count'] = 0
            except:
                business_info['review_count'] = 0
            
            # Extract address
            try:
                address_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]')
                business_info['address'] = address_button.get_attribute('aria-label').replace('Address: ', '').replace('Dirección: ', '')
            except:
                business_info['address'] = 'N/A'
            
            # Extract phone
            try:
                phone_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id*="phone"]')
                phone_text = phone_button.get_attribute('aria-label')
                business_info['phone'] = phone_text.replace('Phone: ', '').replace('Teléfono: ', '')
            except:
                business_info['phone'] = 'N/A'
            
            # Extract website
            try:
                website_button = self.driver.find_element(By.CSS_SELECTOR, 'a[data-item-id="authority"]')
                business_info['website'] = website_button.get_attribute('href')
            except:
                business_info['website'] = 'N/A'
            
            # Extract category
            try:
                category_button = self.driver.find_element(By.CSS_SELECTOR, 'button[jsaction*="category"]')
                business_info['category'] = category_button.text
            except:
                business_info['category'] = 'N/A'
            
            # Extract hours
            try:
                hours_element = self.driver.find_element(By.CSS_SELECTOR, 'div[aria-label*="hours"]')
                business_info['hours'] = hours_element.text
            except:
                business_info['hours'] = 'N/A'
            
            # Extract emails
            emails = self.extract_emails_from_gmb()
            
            # If website exists, try to extract emails from it (with random delay)
            if business_info['website'] != 'N/A' and random.random() > 0.5:  # Only 50% of the time to avoid detection
                self.random_delay(1, 2)
                website_emails = self.extract_emails_from_website(business_info['website'])
                emails.extend(website_emails)
            
            # Remove duplicates and validate emails
            emails = list(set([email for email in emails if self.validate_email(email)]))
            business_info['emails'] = emails if emails else []
            business_info['email'] = emails[0] if emails else 'N/A'
            
            return business_info
            
        except Exception as e:
            logger.error(f"Error extracting business info: {e}")
            return None
    
    def validate_email(self, email):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email.lower()) is not None
    
    def extract_emails_from_gmb(self):
        """Extract emails from GMB page"""
        emails = []
        try:
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            found_emails = re.findall(email_pattern, page_text)
            emails.extend(found_emails)
            
            # Look for mailto links
            try:
                mailto_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="mailto:"]')
                for link in mailto_links:
                    email = link.get_attribute('href').replace('mailto:', '')
                    if email:
                        emails.append(email)
            except:
                pass
                
        except Exception as e:
            logger.debug(f"Error extracting emails from GMB: {e}")
        
        return emails
    
    def extract_emails_from_website(self, url, timeout=5):
        """Extract emails from website"""
        emails = []
        
        if not url or url == 'N/A':
            return emails
            
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents)
            }
            response = requests.get(url, headers=headers, timeout=timeout, verify=False)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                
                page_text = soup.get_text()
                found_emails = re.findall(email_pattern, page_text)
                emails.extend(found_emails)
                
                # Look for mailto links
                mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
                for link in mailto_links:
                    email = link.get('href').replace('mailto:', '').split('?')[0]
                    if email:
                        emails.append(email)
                
        except Exception as e:
            logger.debug(f"Error extracting emails from website {url}: {e}")
        
        # Filter generic emails
        filtered_emails = []
        generic_domains = ['example.com', 'email.com', 'test.com', 'domain.com']
        
        for email in emails:
            email_lower = email.lower()
            if not any(domain in email_lower for domain in generic_domains):
                if '@' in email and '.' in email.split('@')[1]:
                    filtered_emails.append(email)
        
        return filtered_emails
    
    def filter_results(self, businesses, min_rating=0, min_reviews=0, min_age_days=0, max_age_days=36500):
        filtered = []
        for business in businesses:
            if (business.get('rating', 0) >= min_rating and
                business.get('review_count', 0) >= min_reviews):
                filtered.append(business)
        return filtered
    
    def search_location(self, query, department, province, district, **filters):
        location = f"{district}, {province}, {department}"
        logger.info(f"Searching: {query} in {location}")
        
        # Add random delay between locations
        self.random_delay(3, 6)
        
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