# Warewolf - Warehouse Scrapers

This directory contains the scrapers used by the Warewolf application to fetch warehouse data from various sources.

## Structure

- `base_scraper.py` - Abstract base class that defines the common interface and shared functionality for all scrapers
- `warehouse_scraper.py` - A general-purpose HTML scraper for warehouse listings
- `nobroker_scraper.py` - A specialized scraper for the NoBroker platform

## Usage

Import scrapers using the cleaner import syntax:

```python
from app.scrapers import WarehouseScraper, NoBrokerScraper

# Using the general-purpose scraper
warehouse_scraper = WarehouseScraper()
results = await warehouse_scraper.scrape_warehouses(locations=["Mumbai", "Delhi"])

# Using the NoBroker scraper
nobroker_scraper = NoBrokerScraper() 
results = nobroker_scraper.scrape_warehouses(city="Mumbai", min_area=1000)
```

## Extending Scrapers

To create a new scraper for a different platform:

1. Create a new file like `my_platform_scraper.py`
2. Inherit from the `BaseScraper` class
3. Implement the required `scrape_warehouses` method
4. Add your scraper to the imports in `__init__.py`

## Data Format

All scrapers use a standardized data format with the following structure:

```python
{
    "id": int,
    "title": str,
    "location": str,
    "area_sqft": int,
    "price_per_month": float,
    "facilities": List[str],
    "owner_info": {
        "name": str,
        "phone": str,
        "email": str,
        "company": Optional[str],
        "gst_number": Optional[str]
    },
    "description": str,
    "availability": bool,
    "verified": bool
}
```

This ensures consistent data handling across all scraping sources. 