import threading
import time
from src.utils.logger import setup_logger
from src.scrapers.google_company_scraper import GoogleCompanyScraper
from src.web.app import app
import uvicorn

logger = setup_logger("main")

def run_scraper():
    while True:
        try:
            # Test companies - you can modify this list
            companies = [
                "OpenAI",
                "Anthropic",
                "Scale AI",
                "Stability AI",
                "Cohere"
            ]
            
            scraper = GoogleCompanyScraper()
            leads = scraper.scrape(companies)
            
            if leads:
                cleaned_leads = scraper.clean_data(leads)
                scraper.save_data(cleaned_leads)
                logger.info(f"Scraped and saved {len(cleaned_leads)} leads")
            
            # Wait for 4 hours before next scrape
            time.sleep(4 * 60 * 60)
            
        except Exception as e:
            logger.error(f"Error in scraper: {str(e)}")
            time.sleep(300)  # Wait 5 minutes before retry

if __name__ == "__main__":
    # Start scraper in background thread
    scraper_thread = threading.Thread(target=run_scraper)
    scraper_thread.daemon = True
    scraper_thread.start()
    
    # Run web server
    uvicorn.run(app, host="0.0.0.0", port=8000) 