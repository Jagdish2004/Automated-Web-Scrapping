from abc import ABC, abstractmethod
from src.utils.logger import setup_logger

class BaseScraper(ABC):
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)

    @abstractmethod
    def scrape(self):
        """Implement the scraping logic"""
        pass

    @abstractmethod
    def clean_data(self, data):
        """Clean the scraped data"""
        pass

    @abstractmethod
    def save_data(self, data):
        """Save the scraped data"""
        pass 