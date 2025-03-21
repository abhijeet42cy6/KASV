from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from ..scrapers import WarehouseScraper

router = APIRouter(prefix="/warehouse", tags=["Warehouse"])
templates = Jinja2Templates(directory="app/templates")

# Owner information model
class OwnerInfo(BaseModel):
    name: str
    phone: str
    email: EmailStr
    company: Optional[str]
    gst_number: Optional[str]

# Warehouse model with detailed owner information
class Warehouse(BaseModel):
    id: Optional[int] = None
    title: str
    location: str
    area_sqft: int
    price_per_month: float
    facilities: List[str]
    owner_info: OwnerInfo
    description: str
    availability: bool = True
    verified: bool = False

# Temporary database with real-world example data
warehouses_db = [
    Warehouse(
        id=1,
        title="Premium Storage Facility in Delhi Industrial Area",
        location="Delhi, Sector 5, Industrial Area Phase-II",
        area_sqft=5000,
        price_per_month=50000,
        facilities=["24/7 Security", "Loading Dock", "Climate Control", "Fire Safety System", "CCTV Surveillance"],
        owner_info=OwnerInfo(
            name="Rajesh Kumar",
            phone="+91-9876543210",
            email="rajesh.kumar@delhiwarehousing.com",
            company="Delhi Premium Warehousing Pvt Ltd",
            gst_number="07AABCS1429B1Z"
        ),
        description="Modern warehouse facility with 24/7 security and climate control. Ideal for industrial storage with easy highway access.",
        verified=True
    ),
    Warehouse(
        id=2,
        title="Strategic Warehouse in Mumbai Port Area",
        location="Mumbai, Sewri East, Near Port",
        area_sqft=2000,
        price_per_month=30000,
        facilities=["CCTV", "Parking", "Loading/Unloading Area", "Security Personnel"],
        owner_info=OwnerInfo(
            name="Priya Sharma",
            phone="+91-8765432109",
            email="priya.sharma@mumbailogistics.com",
            company="Mumbai Logistics Solutions",
            gst_number="27AAACS9387H1ZV"
        ),
        description="Strategically located warehouse near Mumbai port. Perfect for import-export businesses.",
        verified=True
    )
]

@router.get("/", response_class=HTMLResponse)
async def list_warehouses(request: Request):
    return templates.TemplateResponse(
        "warehouse_list.html", 
        {"request": request, "warehouses": warehouses_db, "current_user": request.state.current_user}
    )

@router.get("/details/{warehouse_id}", response_class=HTMLResponse)
async def warehouse_details(request: Request, warehouse_id: int):
    warehouse = next((w for w in warehouses_db if w.id == warehouse_id), None)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    return templates.TemplateResponse(
        "warehouse_details.html", 
        {"request": request, "warehouse": warehouse, "current_user": request.state.current_user}
    )

@router.get("/add", response_class=HTMLResponse)
async def add_warehouse_form(request: Request):
    return templates.TemplateResponse("add_warehouse.html", {"request": request, "current_user": request.state.current_user})

@router.post("/add")
async def add_warehouse(
    title: str = Form(...),
    location: str = Form(...),
    area_sqft: int = Form(...),
    price_per_month: float = Form(...),
    facilities: str = Form(...),
    owner_name: str = Form(...),
    owner_phone: str = Form(...),
    owner_email: EmailStr = Form(...),
    owner_company: Optional[str] = Form(None),
    owner_gst: Optional[str] = Form(None),
    description: str = Form(...)
):
    # Generate a new ID
    new_id = max([w.id for w in warehouses_db], default=0) + 1
    
    # Create owner info
    owner_info = OwnerInfo(
        name=owner_name,
        phone=owner_phone,
        email=owner_email,
        company=owner_company,
        gst_number=owner_gst
    )
    
    # Create a new warehouse
    new_warehouse = Warehouse(
        id=new_id,
        title=title,
        location=location,
        area_sqft=area_sqft,
        price_per_month=price_per_month,
        facilities=facilities.split(','),
        owner_info=owner_info,
        description=description,
        verified=False  # New warehouses start as unverified
    )
    
    # Add to the database
    warehouses_db.append(new_warehouse)
    
    return {"message": "Warehouse added successfully", "id": new_id}

@router.get("/search", response_class=HTMLResponse)
async def search_form(request: Request):
    return templates.TemplateResponse("search_warehouse.html", {"request": request, "current_user": request.state.current_user})

@router.post("/search")
async def search_warehouses(
    request: Request,
    location: Optional[str] = Form(None),
    min_area: Optional[int] = Form(None),
    max_price: Optional[float] = Form(None)
):
    results = warehouses_db
    
    if location:
        results = [w for w in results if location.lower() in w.location.lower()]
    
    if min_area:
        results = [w for w in results if w.area_sqft >= min_area]
    
    if max_price:
        results = [w for w in results if w.price_per_month <= max_price]
    
    # Return the template instead of JSON
    return templates.TemplateResponse(
        "warehouse_list.html", 
        {"request": request, "warehouses": results, "current_user": request.state.current_user}
    )

# Remove public scraping endpoints
# The scraping functionality remains in the scraper module for internal use only 