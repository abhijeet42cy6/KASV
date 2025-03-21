from typing import List, Dict, Any, Optional
import logging
from abc import ABC, abstractmethod

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Abstract base class for all warehouse scrapers
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9"
        }
        self.results = []
    
    @abstractmethod
    def scrape_warehouses(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        Abstract method that must be implemented by all scraper subclasses
        to scrape warehouse listings from a specific source
        """
        pass
    
    def _extract_number(self, text: str) -> int:
        """Extract numeric value from text"""
        try:
            return int(''.join(filter(str.isdigit, text)))
        except:
            return 0
            
    def _extract_facilities(self, facilities_data) -> List[str]:
        """
        Extract facilities from data, to be implemented by subclasses
        with source-specific implementation
        """
        return [] 