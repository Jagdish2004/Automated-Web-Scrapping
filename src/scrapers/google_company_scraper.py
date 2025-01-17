from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
from src.scrapers.base_scraper import BaseScraper
from src.models.lead import Lead
import pandas as pd
import time
import random
import urllib.parse
import os

class GoogleCompanyScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.setup_driver()
        self.base_url = "https://www.google.com"
        
    def setup_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Add more stealth options
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-notifications')
        
        # Rotate user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            # Add stealth JS
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            self.wait = WebDriverWait(self.driver, 20)
            self.logger.info("Chrome driver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {str(e)}")
            raise

    def search_company(self, query):
        """Search for company information on Google"""
        try:
            # Format search query
            search_query = f"{query} company contact email"
            encoded_query = urllib.parse.quote(search_query)
            self.driver.get(f"{self.base_url}/search?q={encoded_query}")
            time.sleep(random.uniform(2, 4))
            
            # Get search results
            results = self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.g")
            ))
            
            company_info = {
                'name': query,
                'website': None,
                'email': None,
                'description': None,
                'location': None
            }
            
            # Process first few results
            for result in results[:3]:
                try:
                    link = result.find_element(By.CSS_SELECTOR, "a").get_attribute('href')
                    if not company_info['website'] and self._is_company_website(link):
                        company_info['website'] = link
                        
                    # Try to get description
                    if not company_info['description']:
                        try:
                            snippet = result.find_element(By.CSS_SELECTOR, "div.VwiC3b").text
                            company_info['description'] = snippet
                        except:
                            pass
                            
                    # Visit the page to look for email
                    if not company_info['email']:
                        email = self._extract_email_from_website(link)
                        if email:
                            company_info['email'] = email
                            
                except Exception as e:
                    self.logger.error(f"Error processing search result: {str(e)}")
                    continue
                    
            return company_info
            
        except Exception as e:
            self.logger.error(f"Error searching company: {str(e)}")
            return None

    def _is_company_website(self, url):
        """Check if URL likely belongs to company website"""
        low_quality_domains = ['facebook.com', 'linkedin.com', 'twitter.com', 'instagram.com', 
                             'youtube.com', 'crunchbase.com', 'bloomberg.com', 'wikipedia.org']
        return not any(domain in url.lower() for domain in low_quality_domains)

    def _extract_email_from_website(self, website):
        """Extract email from website"""
        try:
            self.driver.get(website)
            time.sleep(random.uniform(2, 3))
            
            # Look for email patterns
            email_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'mailto:')]")
            if email_elements:
                return email_elements[0].get_attribute('href').replace('mailto:', '')
            
            # Look for contact page
            contact_links = self.driver.find_elements(
                By.XPATH,
                "//a[contains(translate(text(), 'CONTACT', 'contact'), 'contact')]"
            )
            if contact_links:
                contact_links[0].click()
                time.sleep(random.uniform(1, 2))
                email_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'mailto:')]")
                if email_elements:
                    return email_elements[0].get_attribute('href').replace('mailto:', '')
            
            return None
        except:
            return None

    def scrape(self, companies):
        """Scrape information for a list of companies"""
        leads = []
        
        try:
            self.logger.info("Starting Google company scraping...")
            
            for company in companies[:10]:  # Limit to 10 companies
                try:
                    self.logger.info(f"Processing company: {company}")
                    
                    company_info = self.search_company(company)
                    if company_info:
                        lead = Lead(
                            name=company_info['name'],
                            email=company_info['email'] or f"contact@{company_info['name'].lower().replace(' ', '')}.com",
                            platform='google',
                            category='business',
                            website=company_info['website'],
                            description=company_info['description'],
                            location=company_info['location'],
                            timestamp=datetime.now()
                        )
                        
                        leads.append(lead)
                        self.logger.info(f"Successfully scraped company: {company}")
                    
                    # Random delay between companies
                    time.sleep(random.uniform(5, 10))
                    
                except Exception as e:
                    self.logger.error(f"Error processing company: {str(e)}")
                    continue
                    
            return leads
            
        except Exception as e:
            self.logger.error(f"Error in scraping: {str(e)}")
            return []
        finally:
            self.driver.quit()
            
    def clean_data(self, leads):
        if not leads:
            return []
            
        df = pd.DataFrame([lead.to_dict() for lead in leads])
        df = df.drop_duplicates(subset=['name', 'email'])
        return [Lead(**row) for row in df.to_dict('records')]
        
    def save_data(self, leads):
        """Save leads to CSV file"""
        if not leads:
            return
        
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Convert leads to DataFrame
            df = pd.DataFrame([
                {
                    'name': lead.name,
                    'email': lead.email,
                    'platform': lead.platform,
                    'category': lead.category,
                    'website': lead.website,
                    'description': lead.description,
                    'location': lead.location,
                    'timestamp': lead.timestamp
                }
                for lead in leads
            ])
            
            # Save to CSV
            output_file = 'data/google_leads.csv'
            df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)
            self.logger.info(f"Saved {len(leads)} leads to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}") 