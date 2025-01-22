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
from typing import List
import json

class GoogleCompanyScraper(BaseScraper):
    def __init__(self, proxy_manager=None):
        super().__init__(proxy_manager)
        self.setup_driver()
        self.base_url = "https://www.google.com"
        
    def setup_driver(self):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--window-size=1920,1080')
                
                # Add proxy if configured
                if self.current_proxy:
                    proxy_str = self.current_proxy['http'].replace('http://', '')
                    chrome_options.add_argument(f'--proxy-server={proxy_str}')
                    self.logger.info(f"Using proxy: {proxy_str}")
                
                # Add stealth options
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument('--disable-notifications')
                
                # Additional options to handle proxy issues
                chrome_options.add_argument('--ignore-certificate-errors')
                chrome_options.add_argument('--ignore-ssl-errors')
                chrome_options.add_argument('--disable-web-security')
                
                # Rotate user agents
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
                ]
                chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
                
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.set_page_load_timeout(30)
                
                # Test the connection
                self.driver.get("https://www.google.com")
                if "google" in self.driver.current_url.lower():
                    self.wait = WebDriverWait(self.driver, 20)
                    self.logger.info("Chrome driver initialized successfully")
                    return
                else:
                    raise Exception("Failed to connect to Google")
                    
            except Exception as e:
                self.logger.error(f"Failed to initialize Chrome driver: {str(e)}")
                retry_count += 1
                if self.proxy_manager:
                    self.current_proxy = self.proxy_manager.get_next_proxy()
                time.sleep(5)
        
        raise Exception("Failed to initialize Chrome driver after maximum retries")

    def handle_proxy_error(self):
        """Handle proxy-related errors"""
        self.proxy_failures += 1
        self.logger.warning(f"Proxy failure count: {self.proxy_failures}")
        
        if self.proxy_failures >= self.max_proxy_failures:
            self.logger.info("Rotating proxy due to failures...")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            
            if self.proxy_manager:
                self.current_proxy = self.proxy_manager.get_next_proxy()
                self.proxy_failures = 0
                self.setup_driver()

    def search_company(self, query):
        """Search for company information on Google"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Format search query
                search_query = f"{query} company contact email"
                encoded_query = urllib.parse.quote(search_query)
                
                # Add error checking for the request
                try:
                    self.driver.get(f"{self.base_url}/search?q={encoded_query}")
                except Exception as e:
                    if any(error in str(e).lower() for error in ['timeout', 'connection reset', 'empty response']):
                        self.handle_proxy_error()
                        retry_count += 1
                        continue
                    raise
                
                # Check for various blocking conditions
                page_source = self.driver.page_source.lower()
                if any(text in page_source for text in [
                    'unusual traffic',
                    'please try your request again',
                    'automated requests',
                    'blocked',
                    'captcha'
                ]):
                    self.logger.warning("Detected blocking/captcha")
                    self.handle_proxy_error()
                    retry_count += 1
                    continue
                
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
                retry_count += 1
                if any(error in str(e).lower() for error in [
                    'proxy', 'timeout', 'connection reset',
                    'empty response', 'connection refused'
                ]):
                    self.handle_proxy_error()
                time.sleep(random.uniform(5, 10))
        
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

    def scrape(self, companies: List[str]) -> List[Lead]:
        """Scrape company information"""
        leads = []
        total = len(companies)
        start_time = time.time()
        
        self.logger.info(f"Starting scrape of {total} companies")
        
        # Create progress file
        with open('data/scraping_progress.json', 'w') as f:
            json.dump({
                'total': total,
                'completed': 0,
                'successful': 0,
                'failed': 0,
                'start_time': start_time,
                'current_company': ''
            }, f)
        
        for idx, company in enumerate(companies, 1):
            try:
                # Update progress
                self._update_progress(idx, total, company)
                
                # Search for company info
                company_info = self.search_company(company)
                if company_info and company_info.get('email'):
                    lead = Lead(
                        name=company_info['name'],
                        email=company_info['email'],
                        platform='google',
                        category='business',
                        website=company_info['website'],
                        description=company_info['description'],
                        location=company_info['location'],
                        timestamp=datetime.now()
                    )
                    leads.append(lead)
                    
                    # Save leads in real-time
                    self._save_lead(lead)
                    
                # Calculate and log progress
                elapsed = time.time() - start_time
                rate = idx / (elapsed / 3600)
                self._log_progress(idx, total, rate, len(leads))
                
            except Exception as e:
                self.logger.error(f"Error processing {company}: {str(e)}")
                continue
        
        return leads

    def _update_progress(self, current: int, total: int, company: str):
        """Update progress file"""
        try:
            with open('data/scraping_progress.json', 'r') as f:
                progress = json.load(f)
                
            progress.update({
                'completed': current,
                'current_company': company,
                'last_update': time.time()
            })
            
            with open('data/scraping_progress.json', 'w') as f:
                json.dump(progress, f)
                
        except Exception as e:
            self.logger.error(f"Error updating progress: {e}")

    def _save_lead(self, lead: Lead):
        """Save a single lead to CSV"""
        try:
            df = pd.DataFrame([lead.to_dict()])
            output_file = 'data/google_leads.csv'
            df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)
            self.logger.info(f"Saved lead for {lead.name}")
        except Exception as e:
            self.logger.error(f"Error saving lead: {e}")

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

    def _log_progress(self, current: int, total: int, rate: float, leads_found: int):
        """Log scraping progress"""
        try:
            # Update progress file
            with open('data/scraping_progress.json', 'r') as f:
                progress = json.load(f)
                
            progress.update({
                'completed': current,
                'successful': leads_found,
                'failed': current - leads_found,
                'rate': round(rate, 2),
                'last_update': time.time()
            })
            
            with open('data/scraping_progress.json', 'w') as f:
                json.dump(progress, f)
                
            # Log progress
            percent_complete = (current / total) * 100
            self.logger.info(
                f"Progress: {current}/{total} ({percent_complete:.1f}%) - "
                f"Found {leads_found} leads - Rate: {rate:.1f} companies/hour"
            )
            
        except Exception as e:
            self.logger.error(f"Error logging progress: {e}") 