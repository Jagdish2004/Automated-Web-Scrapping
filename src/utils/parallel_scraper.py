from concurrent.futures import ThreadPoolExecutor
from typing import List
from src.scrapers.google_company_scraper import GoogleCompanyScraper
from src.utils.proxy_manager import ProxyManager

def parallel_scrape(companies: List[str], num_workers: int = 3):
    """Scrape companies in parallel"""
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        proxy_manager = ProxyManager()
        chunks = chunk_companies(companies, len(companies) // num_workers)
        
        futures = []
        for chunk in chunks:
            scraper = GoogleCompanyScraper(proxy_manager=proxy_manager)
            future = executor.submit(scraper.scrape, chunk)
            futures.append(future)
        
        all_leads = []
        for future in futures:
            leads = future.result()
            all_leads.extend(leads)
            
    return all_leads 