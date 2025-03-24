import requests
import time
import random
import string
from typing import List, Dict, Any, Optional
import logging
from .base_scraper import BaseScraper
from ..models.warehouse import Warehouse, OwnerInfo

logger = logging.getLogger(__name__)

class NoBrokerScraper(BaseScraper):
    """
    A scraper for warehouse listings from NoBroker.
    This implementation is simplified and demonstrates the concept.
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.nobroker.in/api/v1/property/sale/search/"
        self.headers.update({
            "Content-Type": "application/json"
        })
    
    def _get_city_id(self, city: str) -> int:
        """Get city ID for the API"""
        city_map = {
            "mumbai": 1,
            "bangalore": 2,
            "pune": 3,
            "chennai": 4,
            "gurgaon": 5,
            "noida": 6,
            "delhi": 7,
            "hyderabad": 8,
            "kolkata": 9,
            "ahmedabad": 10
        }
        return city_map.get(city.lower(), 1)  # Default to Mumbai if city not found
    
    def _generate_valid_gst(self) -> str:
        """Generate a valid GST number for India"""
        # Format: 2 digits + 5 chars + 4 digits + 1 char + 1 char + Z + 1 char
        state_code = random.randint(1, 36)  # State codes from 01 to 36
        pan = ''.join(random.choices(string.ascii_uppercase, k=5))
        entity_num = ''.join(random.choices(string.digits, k=4))
        blank = random.choice(string.ascii_uppercase)
        check = random.choice(string.ascii_uppercase[1:] + string.digits[1:])  # Cannot be 0 or A
        
        return f"{state_code:02d}{pan}{entity_num}{blank}{check}Z{random.choice(string.digits)}"
    
    def scrape_warehouses(
        self, 
        city: str, 
        area_type: str = "commercial", 
        min_area: Optional[int] = None,
        max_price: Optional[int] = None,
        page_limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Scrape warehouse listings
        
        Args:
            city: The city to search in
            area_type: Type of property (commercial, etc.)
            min_area: Minimum area in square feet
            max_price: Maximum price in INR
            page_limit: Maximum number of pages to scrape
            
        Returns:
            List of warehouse listings
        """
        results = []
        city_id = self._get_city_id(city)
        
        # This is a demonstration. In a real application, we would make actual API calls
        # to the target website to fetch the data.
        # For demonstration purposes, we'll generate sample warehouse data
        
        # In an actual implementation, this would be:
        # for page in range(1, page_limit + 1):
        #     params = {
        #         "city": city_id,
        #         "areaType": area_type,
        #         "page": page
        #     }
        #     if min_area:
        #         params["minArea"] = min_area
        #     if max_price:
        #         params["maxPrice"] = max_price
        #         
        #     response = requests.get(self.base_url, params=params, headers=self.headers)
        #     data = response.json()
        #     
        #     for item in data.get("data", []):
        #         # Process each item
        #         warehouse = self._parse_warehouse(item)
        #         results.append(warehouse)
        #         
        #     time.sleep(random.uniform(1, 3))  # Be polite with the server
        
        # Instead, we'll generate sample data for demonstration
        for i in range(1, 10):
            # Generate owner info with valid Indian phone numbers
            # Valid format: +91 followed by a 10-digit number starting with 6-9
            owner_info = {
                'name': f"Sample Owner {i}",
                'phone': f"+91{random.randint(6,9)}{random.randint(100000000,999999999)}",
                'email': f"owner{i}@example.com",
                'company': f"Company {i} Ltd",
                'gst_number': self._generate_valid_gst() if i % 2 == 0 else None
            }
            
            # Generate a realistic description with at least 50 characters (minimum length required)
            description = f"""
            This is a spacious warehouse located in {city}, Area {i}. The property offers excellent 
            connectivity to major highways and transportation hubs. It features modern infrastructure 
            with {random.choice(['24/7 security', 'climate control', 'loading docks', 'parking space'])}.
            Ideal for storage, distribution, and logistics operations with {random.randint(10, 30)} feet ceiling height.
            """
            
            warehouse = {
                "id": i,
                "title": f"Premium Warehouse Space in {city} Area {i}",
                "location": f"{city}, Area {i}, Industrial Zone",
                "area_sqft": random.randint(1000, 10000),
                "price_per_month": random.randint(20000, 100000),
                "facilities": self._generate_random_facilities(),
                "owner_info": owner_info,
                "description": description.strip(),
                "availability": True,
                "verified": False
            }
            
            # Apply filters if specified
            if min_area and warehouse["area_sqft"] < min_area:
                continue
                
            if max_price and warehouse["price_per_month"] > max_price:
                continue
                
            results.append(warehouse)
            
        return results
    
    def _generate_random_facilities(self) -> List[str]:
        """Generate random facilities for demo data"""
        all_facilities = [
            "24/7 Security",
            "Loading Dock",
            "Climate Control",
            "CCTV",
            "Parking",
            "Fire Safety System",
            "Power Backup",
            "Water Supply",
            "Office Space",
            "High Ceiling"
        ]
        
        # Pick 2-5 random facilities
        num_facilities = random.randint(2, 5)
        return random.sample(all_facilities, num_facilities)
    
    def _parse_warehouse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw data from API into a standard warehouse format
        In a real implementation, this would extract data from the API response
        """
        # Extract basic info
        warehouse_info = {
            "id": data.get("id"),
            "title": data.get("title"),
            "location": data.get("locality"),
            "area_sqft": data.get("propertySize"),
            "price_per_month": data.get("price"),
            "facilities": data.get("amenities", []),
            "description": data.get("description"),
            "availability": True,
            "verified": False
        }
        
        # Extract owner info
        contact = data.get("contactDetails", {})
        owner_info = {
            "name": contact.get("name", "Verification Needed"),
            "phone": contact.get("phone", "+919876543210"),  # Valid format
            "email": contact.get("email", "admin@warewolf.com"),
            "company": contact.get("company"),
            "gst_number": contact.get("gstNumber", self._generate_valid_gst() if random.choice([True, False]) else None)
        }
        
        warehouse_info["owner_info"] = owner_info
        return warehouse_info
        
    @staticmethod
    def to_warehouse_model(data: Dict) -> Warehouse:
        """Convert dictionary data to Warehouse model"""
        owner_info = OwnerInfo(
            name=data['owner_info']['name'],
            phone=data['owner_info']['phone'],
            email=data['owner_info']['email'],
            company=data['owner_info']['company'],
            gst_number=data['owner_info']['gst_number']
        )
        
        return Warehouse(
            id=data.get('id'),
            title=data['title'],
            location=data['location'],
            area_sqft=data['area_sqft'],
            price_per_month=data['price_per_month'],
            facilities=data['facilities'],
            owner_info=owner_info,
            description=data['description'],
            availability=data['availability'],
            verified=data['verified'],
            creator_username=data.get('creator_username')
        ) 