import threading
import time
from src.utils.logger import setup_logger
from src.scrapers.google_company_scraper import GoogleCompanyScraper
from src.web.app import app
import uvicorn
from src.utils.proxy_manager import ProxyManager
import pandas as pd
from typing import List
import random
from src.utils.company_collector import CompanyCollector

logger = setup_logger("main")

def load_target_companies() -> List[str]:
    """Load target companies from various sources"""
    companies = []
    
    try:
        # Use company collector to get companies
        collector = CompanyCollector()
        companies_by_industry = collector.collect_companies()
        
        # Flatten the dictionary into a list
        for industry_companies in companies_by_industry.values():
            companies.extend(industry_companies)
        
        # Remove duplicates and shuffle
        companies = list(set(companies))
        random.shuffle(companies)
        
        logger.info(f"Loaded {len(companies)} companies across {len(companies_by_industry)} industries")
        return companies
        
    except Exception as e:
        logger.error(f"Error loading companies: {e}")
        
        # Fallback to basic company list if collection fails
        return [
            "OpenAI", "Anthropic", "Scale AI", "Stability AI", "Cohere",
            "Microsoft", "Google", "Amazon", "Meta", "Apple", "Netflix", "Tesla",
            # ... add more fallback companies
        ]

def chunk_companies(companies: List[str], chunk_size: int = 50) -> List[List[str]]:
    """Split companies into smaller chunks"""
    return [companies[i:i + chunk_size] for i in range(0, len(companies), chunk_size)]

def run_scraper():
    while True:
        try:
            # Initialize proxy manager
            proxy_manager = ProxyManager()
            
            # Load and chunk companies
            all_companies = load_target_companies()
            company_chunks = chunk_companies(all_companies, chunk_size=20)  # Smaller chunks
            
            logger.info(f"Loaded {len(all_companies)} companies to scrape")
            
            for chunk in company_chunks:
                try:
                    scraper = GoogleCompanyScraper(proxy_manager=proxy_manager)
                    leads = scraper.scrape(chunk)
                    
                    if leads:
                        cleaned_leads = scraper.clean_data(leads)
                        scraper.save_data(cleaned_leads)
                        logger.info(f"Scraped and saved {len(cleaned_leads)} leads")
                    
                    # Shorter delay between chunks
                    time.sleep(random.uniform(30, 60))  # 30-60 seconds delay
                    
                except Exception as e:
                    logger.error(f"Error processing chunk: {str(e)}")
                    time.sleep(10)  # Short delay on error
                    continue
                finally:
                    # Clean up resources
                    if scraper and scraper.driver:
                        try:
                            scraper.driver.quit()
                        except:
                            pass
            
            # Shorter interval between cycles
            time.sleep(300)  # 5 minutes between cycles
            
        except Exception as e:
            logger.error(f"Error in scraper: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    # Start scraper in background thread
    scraper_thread = threading.Thread(target=run_scraper)
    scraper_thread.daemon = True
    scraper_thread.start()
    
    # Run web server
    uvicorn.run(app, host="0.0.0.0", port=8000) 