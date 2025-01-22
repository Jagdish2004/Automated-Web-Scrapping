from abc import ABC, abstractmethod
from src.utils.logger import setup_logger
from typing import Dict, Optional

class BaseScraper(ABC):
    def __init__(self, proxy_manager=None):
        self.logger = setup_logger(self.__class__.__name__)
        self.proxy_manager = proxy_manager
        self.current_proxy = None
        self.proxy_failures = 0
        self.max_proxy_failures = 3  # Maximum failures before rotating proxy

    def set_proxy(self, proxy: Dict[str, str]) -> None:
        """Set proxy configuration"""
        self.proxy = proxy
        self.logger.info(f"Set new proxy configuration: {proxy.get('http', '')}")
        
    def rotate_proxy(self) -> None:
        """Rotate to next proxy"""
        if self.proxy_manager:
            self.current_proxy = self.proxy_manager.get_next_proxy()
            self.proxy_failures = 0
            self.logger.info(f"Rotated to new proxy: {self.current_proxy['http']}")

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