from src.scrapers.google_company_scraper import GoogleCompanyScraper
from src.utils.proxy_manager import ProxyManager
from src.utils.logger import setup_logger
import time

logger = setup_logger("scraper")

def start_scraping():
    """Start the scraping process"""
    try:
        # Initialize
        proxy_manager = ProxyManager()
        scraper = GoogleCompanyScraper(proxy_manager=proxy_manager)
        
        # Get test companies
        test_companies = [
            "OpenAI", "Anthropic", "Scale AI", "Stability AI", "Cohere",
            "Microsoft", "Google", "Amazon", "Meta", "Apple"
        ]
        
        # Run scraper
        logger.info("Starting test scrape...")
        leads = scraper.scrape(test_companies)
        
        if leads:
            cleaned_leads = scraper.clean_data(leads)
            scraper.save_data(cleaned_leads)
            logger.info(f"Successfully scraped {len(cleaned_leads)} leads")
            
    except Exception as e:
        logger.error(f"Error in scraping: {e}")
    finally:
        if scraper and scraper.driver:
            scraper.driver.quit()

if __name__ == "__main__":
    start_scraping() 