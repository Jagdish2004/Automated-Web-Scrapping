import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from src.utils.gemini_helper import GeminiHelper
from src.utils.logger import setup_logger

logger = setup_logger("company_collector")

class CompanyCollector:
    def __init__(self):
        self.gemini = GeminiHelper()
        self.companies_by_industry: Dict[str, List[str]] = {}
        
    def collect_companies(self) -> Dict[str, List[str]]:
        """Collect companies using Gemini AI"""
        try:
            # Get initial companies by industry
            logger.info("Collecting initial companies from Gemini...")
            self.companies_by_industry = self.gemini.get_industries_and_companies()
            
            # Expand each industry's company list
            for industry, companies in self.companies_by_industry.items():
                logger.info(f"Expanding company list for {industry}...")
                additional_companies = self.gemini.expand_company_list(industry, companies)
                self.companies_by_industry[industry].extend(additional_companies)
                
            # Try to add stock market companies if yfinance is available
            try:
                import yfinance as yf
                stock_companies = self.collect_from_stock_markets()
                self.companies_by_industry['Public Companies'] = stock_companies
                logger.info(f"Added {len(stock_companies)} public companies")
            except ImportError:
                logger.warning("yfinance not installed, skipping stock market companies")
                
            # Save to CSV
            self._save_to_csv()
            
            return self.companies_by_industry
            
        except Exception as e:
            logger.error(f"Error collecting companies: {e}")
            return {}
    
    def _save_to_csv(self):
        """Save collected companies to CSV files"""
        try:
            # Save all companies to one file
            all_companies = []
            for industry, companies in self.companies_by_industry.items():
                for company in companies:
                    all_companies.append({
                        'company_name': company,
                        'industry': industry
                    })
            
            df = pd.DataFrame(all_companies)
            df.to_csv('data/target_companies.csv', index=False)
            logger.info(f"Saved {len(all_companies)} companies to target_companies.csv")
            
            # Save separate files by industry
            for industry, companies in self.companies_by_industry.items():
                df = pd.DataFrame({'company_name': companies})
                filename = f'data/companies_{industry.lower().replace(" ", "_")}.csv'
                df.to_csv(filename, index=False)
                logger.info(f"Saved {len(companies)} companies to {filename}")
                
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")

    def collect_from_stock_markets(self) -> List[str]:
        """Collect companies from stock markets"""
        companies = set()
        
        try:
            # Get S&P 500 companies
            sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
            companies.update(sp500['Security'].tolist())
            
            # Get NASDAQ companies
            nasdaq = pd.read_html('https://en.wikipedia.org/wiki/NASDAQ-100')[4]
            companies.update(nasdaq['Company'].tolist())
            
        except Exception as e:
            logger.error(f"Error collecting stock market companies: {e}")
            
        return list(companies)

def collect_from_crunchbase() -> List[str]:
    # Implement CrunchBase collection logic
    pass

def collect_from_linkedin() -> List[str]:
    # Implement LinkedIn collection logic
    pass

def collect_from_stock_markets() -> List[str]:
    companies = []
    
    # Get S&P 500 companies
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    companies.extend(sp500['Security'].tolist())
    
    # Get NASDAQ companies
    nasdaq = pd.read_html('https://en.wikipedia.org/wiki/NASDAQ-100')[4]
    companies.extend(nasdaq['Company'].tolist())
    
    return companies 