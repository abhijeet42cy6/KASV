import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime
from ..models.warehouse import Warehouse, OwnerInfo
from .base_scraper import BaseScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WarehouseScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.headers.update({
            'Content-Type': 'text/html; charset=utf-8'
        })

    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        try:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.text()
                logger.warning(f"Failed to fetch {url}, status: {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def parse_warehouse(self, html_content: str) -> List[Dict]:
        soup = BeautifulSoup(html_content, 'html.parser')
        warehouses = []
        
        for container in soup.find_all('div', class_="card"):
            try:
                # Extract owner information from the listing
                owner_info = self._extract_owner_info(container)
                
                warehouse = {
                    'title': container.find('h2').text.strip(),
                    'location': container.find('h5').text.strip(),
                    'area_sqft': self._extract_number(container.find_all('h3')[0].text),
                    'price_per_month': self._extract_number(container.find_all('h3')[2].text),
                    'facilities': self._extract_facilities(container),
                    'description': container.find('div', class_='detail-summary').text.strip(),
                    'availability': True,
                    'owner_info': owner_info,
                    'verified': False  # Scraped listings start as unverified
                }
                warehouses.append(warehouse)
            except Exception as e:
                logger.error(f"Error parsing warehouse: {str(e)}")
                continue
                
        return warehouses

    def _extract_owner_info(self, container) -> Dict:
        """Extract owner information from the listing."""
        try:
            owner_div = container.find('div', class_='owner-info')
            if owner_div:
                return {
                    'name': owner_div.find('span', class_='owner-name').text.strip(),
                    'phone': owner_div.find('span', class_='owner-phone').text.strip(),
                    'email': owner_div.find('span', class_='owner-email').text.strip(),
                    'company': owner_div.find('span', class_='owner-company').text.strip(),
                    'gst_number': owner_div.find('span', class_='owner-gst').text.strip()
                }
        except Exception as e:
            logger.error(f"Error extracting owner info: {str(e)}")
        
        # Return placeholder data that needs verification
        return {
            'name': "Verification Needed",
            'phone': "Contact Admin",
            'email': "admin@warewolf.com",
            'company': None,
            'gst_number': None
        }

    def _extract_number(self, text: str) -> int:
        try:
            return int(''.join(filter(str.isdigit, text)))
        except:
            return 0

    def _extract_facilities(self, container) -> List[str]:
        facilities = []
        try:
            facility_div = container.find('div', class_='detail-summary')
            if facility_div:
                for item in facility_div.find_all('h5'):
                    facilities.append(item.text.strip())
        except Exception:
            pass
        return facilities

    async def scrape_warehouses(self, locations: List[str], max_pages: int = 5) -> List[Dict]:
        all_warehouses = []
        
        async with aiohttp.ClientSession() as session:
            for location in locations:
                logger.info(f"Scraping warehouses in {location}")
                
                for page in range(max_pages):
                    url = self._build_url(location, page + 1)
                    html_content = await self.fetch_page(session, url)
                    
                    if html_content:
                        warehouses = self.parse_warehouse(html_content)
                        all_warehouses.extend(warehouses)
                        await asyncio.sleep(1)
                    else:
                        break

        return all_warehouses

    def _build_url(self, location: str, page: int) -> str:
        # This method should be implemented with actual website URL structure
        base_url = "https://example.com/warehouses"
        return f"{base_url}?location={location}&page={page}"

    def save_to_csv(self, warehouses: List[Dict], filename: str):
        df = pd.DataFrame(warehouses)
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(warehouses)} warehouses to {filename}")

    @staticmethod
    def to_warehouse_model(data: Dict) -> Warehouse:
        owner_info = OwnerInfo(
            name=data['owner_info']['name'],
            phone=data['owner_info']['phone'],
            email=data['owner_info']['email'],
            company=data['owner_info']['company'],
            gst_number=data['owner_info']['gst_number']
        )
        
        return Warehouse(
            title=data['title'],
            location=data['location'],
            area_sqft=data['area_sqft'],
            price_per_month=data['price_per_month'],
            facilities=data['facilities'],
            owner_info=owner_info,
            description=data['description'],
            availability=data['availability'],
            verified=data['verified']
        ) 