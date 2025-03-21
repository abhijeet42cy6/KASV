from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any, Optional
from ..scrapers import NoBrokerScraper

router = APIRouter(prefix="/scraping", tags=["Scraping"])
templates = Jinja2Templates(directory="app/templates")

# Store scraped results
scraped_warehouses = []

@router.get("/", response_class=HTMLResponse)
async def scraping_dashboard(request: Request):
    return templates.TemplateResponse(
        "scraping_dashboard.html", 
        {"request": request, "warehouses": scraped_warehouses, "current_user": request.state.current_user}
    )

@router.post("/run")
async def run_scraper(
    background_tasks: BackgroundTasks,
    city: str = Form(...),
    area_type: str = Form(...),
    min_area: Optional[int] = Form(None),
    max_price: Optional[int] = Form(None)
):
    # Create function to run in background
    def scrape_warehouses():
        global scraped_warehouses
        scraper = NoBrokerScraper()
        results = scraper.scrape_warehouses(
            city=city,
            area_type=area_type,
            min_area=min_area,
            max_price=max_price
        )
        
        # Add results to our storage
        scraped_warehouses = results
    
    # Run scraping in background
    background_tasks.add_task(scrape_warehouses)
    
    return {"message": "Scraping started in the background"}

@router.get("/results")
async def get_scraped_results():
    return {"warehouses": scraped_warehouses}

@router.post("/import")
async def import_to_database():
    # This would import scraped warehouses into your main database
    # For demonstration, we're just returning the count
    return {"message": f"Imported {len(scraped_warehouses)} warehouses"}

@router.get("/cities")
async def get_available_cities():
    # In a real application, this would come from the scraper
    return {
        "cities": [
            "Mumbai", "Delhi", "Bangalore", "Hyderabad", 
            "Chennai", "Kolkata", "Pune", "Ahmedabad"
        ]
    } 