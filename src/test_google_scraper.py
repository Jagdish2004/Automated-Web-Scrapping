import os
from src.utils.logger import setup_logger
from src.scrapers.google_company_scraper import GoogleCompanyScraper
import pandas as pd

logger = setup_logger("test_google_scraper")

def test_google_scraping():
    try:
        # Ensure directories exist
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        logger.info("Starting Google scraping test...")
        
        # Test companies - AI and Tech focused
        companies = [
            "OpenAI",
            "Anthropic",
            "Scale AI",
            "Stability AI",
            "Cohere",
            "Hugging Face",
            "DeepMind",
            "Nvidia",
            "Meta AI",
            "Google Brain"
        ]
        
        # Initialize scraper
        scraper = GoogleCompanyScraper()
        
        # Run scraping
        leads = scraper.scrape(companies)
        
        if leads:
            logger.info(f"Found {len(leads)} leads")
            
            # Print all leads details
            for i, lead in enumerate(leads, 1):
                logger.info(f"\nLead {i}:")
                logger.info(f"Name: {lead.name}")
                logger.info(f"Email: {lead.email}")
                logger.info(f"Website: {lead.website}")
                logger.info(f"Description: {lead.description[:200]}..." if lead.description else "No description")
                logger.info(f"Location: {lead.location}")
            
            # Clean and save the leads
            cleaned_leads = scraper.clean_data(leads)
            scraper.save_data(cleaned_leads)
            logger.info(f"\nSaved {len(cleaned_leads)} leads to data/google_leads.csv")
            
            # Verify saved data
            if os.path.exists('data/google_leads.csv'):
                df = pd.read_csv('data/google_leads.csv')
                logger.info(f"\nVerifying saved data:")
                logger.info(f"Number of saved leads: {len(df)}")
                logger.info(f"Columns: {df.columns.tolist()}")
                logger.info("\nFirst few saved leads:")
                print(df.head().to_string())
            else:
                logger.error("CSV file not found after saving!")
        else:
            logger.warning("No leads found!")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_google_scraping() 