from fastapi import APIRouter, HTTPException, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional, Dict
from pydantic import BaseModel, EmailStr, Field, ValidationError
from ..scrapers import WarehouseScraper, NoBrokerScraper
from ..auth.utils import login_required
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.warehouse import Warehouse, OwnerInfo

router = APIRouter(prefix="/warehouse", tags=["Warehouse"])
templates = Jinja2Templates(directory="app/templates")

# Import scraper results from the scraping module
from .scraping import scraped_warehouses

# Owner information model
class OwnerInfo(BaseModel):
    name: str
    phone: str
    email: EmailStr
    company: Optional[str] = None
    gst_number: Optional[str] = None
    
    model_config = {
        "extra": "forbid"
    }

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
    creator_username: Optional[str] = None  # Track the username of who created this listing
    
    model_config = {
        "extra": "forbid"
    }

# Database for user-created warehouses (empty initially)
real_warehouses_db = []

# Initialize with some sample data for development if empty
if not real_warehouses_db:
    # Create a NoBroker scraper to get some initial data
    scraper = NoBrokerScraper()
    
    # Get sample data for common cities
    sample_data = scraper.scrape_warehouses(
        city="Delhi",  # Sample city
        area_type="commercial",
        min_area=1000,
        max_price=100000
    )
    
    # Convert to warehouse models and add to database
    for data in sample_data:
        warehouse = scraper.to_warehouse_model(data)
        real_warehouses_db.append(warehouse)

# Public warehouse list - shows all warehouses (both limited and full list based on auth)
@router.get("/", response_class=HTMLResponse, name="warehouse_list")
async def list_warehouses(request: Request):
    # Check if user is authenticated
    is_authenticated = hasattr(request.state, "current_user") and request.state.current_user is not None
    
    # For this route, we only show real warehouses created by users
    displayed_warehouses = real_warehouses_db if is_authenticated else real_warehouses_db[:3]
    
    return templates.TemplateResponse(
        "warehouse_list.html", 
        {
            "request": request, 
            "warehouses": displayed_warehouses,
            "current_user": request.state.current_user,
            "is_limited": not is_authenticated and len(real_warehouses_db) > 3,
            "total_count": len(real_warehouses_db)
        }
    )

# Public warehouse details page
@router.get("/details/{warehouse_id}", response_class=HTMLResponse, name="warehouse_details")
async def warehouse_details(request: Request, warehouse_id: int):
    # Find the warehouse with the given ID
    for warehouse in real_warehouses_db:
        if warehouse.id == warehouse_id:
            # Check if current user is the creator of this warehouse
            is_creator = False
            if hasattr(request.state, "current_user") and request.state.current_user:
                is_creator = warehouse.creator_username == request.state.current_user.username
            
            return templates.TemplateResponse(
                "warehouse_details.html", 
                {
                    "request": request, 
                    "warehouse": warehouse, 
                    "current_user": request.state.current_user,
                    "is_creator": is_creator
                }
            )
    
    # If not found, raise a 404 error
    raise HTTPException(status_code=404, detail="Warehouse not found")

# Protected route - Add warehouse form requires login
@router.get("/add", response_class=HTMLResponse, name="warehouse_add")
@login_required
async def add_warehouse_form(request: Request):
    """Display the form to add a new warehouse."""
    print(f"[DEBUG] Inside add_warehouse_form function with request: {request}")
    try:
        current_user = request.state.current_user
        print(f"[DEBUG] Current user in handler: {current_user.username if current_user else 'None'}")
        return templates.TemplateResponse(
            "add_warehouse.html", 
            {"request": request, "current_user": current_user}
        )
    except Exception as e:
        print(f"[DEBUG] Error in add_warehouse_form: {str(e)}")
        raise

# Protected route - Add warehouse submission requires login
@router.post("/add")
@login_required
async def add_warehouse(
    request: Request,
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
    try:
        # Generate a new ID
        new_id = 1
        if real_warehouses_db:
            new_id = max([w.id for w in real_warehouses_db]) + 1
        
        # Create owner information
        owner = OwnerInfo(
            name=owner_name,
            phone=owner_phone,
            email=owner_email,
            company=owner_company,
            gst_number=owner_gst
        )
        
        # Create new warehouse with creator information
        new_warehouse = Warehouse(
            id=new_id,
            title=title,
            location=location,
            area_sqft=area_sqft,
            price_per_month=price_per_month,
            facilities=facilities.split(","),
            owner_info=owner,
            description=description,
            availability=True,
            verified=False,
            creator_username=request.state.current_user.username
        )
        
        # Add to database
        real_warehouses_db.append(new_warehouse)
        
        # Redirect to the warehouse list page
        return RedirectResponse(url="/warehouse/", status_code=303)
    
    except ValidationError as e:
        # Convert validation errors to a user-friendly format
        errors: Dict[str, str] = {}
        for error in e.errors():
            field = error["loc"][0]
            message = error["msg"]
            errors[field] = message
        
        # Return the form with errors
        return templates.TemplateResponse(
            "add_warehouse.html",
            {
                "request": request,
                "current_user": request.state.current_user,
                "errors": errors,
                "form_data": {
                    "title": title,
                    "location": location,
                    "area_sqft": area_sqft,
                    "price_per_month": price_per_month,
                    "facilities": facilities,
                    "owner_name": owner_name,
                    "owner_phone": owner_phone,
                    "owner_email": owner_email,
                    "owner_company": owner_company,
                    "owner_gst": owner_gst,
                    "description": description
                }
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

# New route - Edit warehouse (only for creators)
@router.get("/edit/{warehouse_id}", response_class=HTMLResponse, name="warehouse_edit")
@login_required
async def edit_warehouse_form(request: Request, warehouse_id: int):
    """Display form to edit an existing warehouse (only accessible by the creator)"""
    # Find the warehouse with the given ID
    warehouse = None
    for w in real_warehouses_db:
        if w.id == warehouse_id:
            warehouse = w
            break
    
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    # Check if current user is the creator
    if warehouse.creator_username != request.state.current_user.username:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to edit this warehouse listing"
        )
    
    # Render the edit form with the warehouse data
    return templates.TemplateResponse(
        "edit_warehouse.html",
        {
            "request": request,
            "warehouse": warehouse,
            "current_user": request.state.current_user,
            "facilities_str": ", ".join(warehouse.facilities)
        }
    )

# Process warehouse edit submission
@router.post("/edit/{warehouse_id}")
@login_required
async def edit_warehouse(
    request: Request,
    warehouse_id: int,
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
    try:
        # Find the warehouse with the given ID
        warehouse_index = None
        for i, w in enumerate(real_warehouses_db):
            if w.id == warehouse_id:
                warehouse_index = i
                break
        
        if warehouse_index is None:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        
        # Check if current user is the creator
        if real_warehouses_db[warehouse_index].creator_username != request.state.current_user.username:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to edit this warehouse listing"
            )
        
        # Update owner information
        owner = OwnerInfo(
            name=owner_name,
            phone=owner_phone,
            email=owner_email,
            company=owner_company,
            gst_number=owner_gst
        )
        
        # Create updated warehouse while preserving the original ID and creator
        updated_warehouse = Warehouse(
            id=warehouse_id,
            title=title,
            location=location,
            area_sqft=area_sqft,
            price_per_month=price_per_month,
            facilities=facilities.split(","),
            owner_info=owner,
            description=description,
            availability=True,
            verified=real_warehouses_db[warehouse_index].verified,
            creator_username=request.state.current_user.username
        )
        
        # Replace the old warehouse with the updated one
        real_warehouses_db[warehouse_index] = updated_warehouse
        
        # Redirect to the warehouse details page
        return RedirectResponse(url=f"/warehouse/details/{warehouse_id}", status_code=303)
    
    except ValidationError as e:
        # Convert validation errors to a user-friendly format
        errors: Dict[str, str] = {}
        for error in e.errors():
            field = error["loc"][0]
            message = error["msg"]
            errors[field] = message
        
        # Get the current warehouse data
        warehouse = real_warehouses_db[warehouse_index]
        
        # Return the form with errors
        return templates.TemplateResponse(
            "edit_warehouse.html",
            {
                "request": request,
                "warehouse": warehouse,
                "current_user": request.state.current_user,
                "errors": errors,
                "facilities_str": facilities
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

# Protected route - Search form requires login
@router.get("/search", response_class=HTMLResponse, name="warehouse_search")
@login_required
async def search_form(request: Request):
    return templates.TemplateResponse("search_warehouse.html", {"request": request, "current_user": request.state.current_user})

# Protected route - Search requires login
@router.post("/search", name="warehouse_search_results")
@login_required
async def search_warehouses(
    request: Request,
    location: Optional[str] = Form(None),
    min_area: Optional[int] = Form(None),
    max_price: Optional[float] = Form(None),
    facilities: Optional[List[str]] = Form(None),
    availability: Optional[str] = Form(None)
):
    # Combine all warehouse sources
    all_warehouses = real_warehouses_db.copy()
    
    # Add scraped warehouses to the results if available
    if scraped_warehouses:
        scraper = NoBrokerScraper()
        for warehouse_data in scraped_warehouses:
            try:
                # Convert to Warehouse model
                warehouse = scraper.to_warehouse_model(warehouse_data)
                all_warehouses.append(warehouse)
            except Exception as e:
                print(f"Error converting scraped warehouse: {str(e)}")
    
    # If no location specified, perform a real-time scraping
    if not location and not min_area and not max_price and len(all_warehouses) < 5:
        try:
            # Perform a real-time scrape for more warehouses
            scraper = NoBrokerScraper()
            
            # Get warehouses for common cities
            for city in ["Mumbai", "Delhi", "Bangalore", "Hyderabad"]:
                results = scraper.scrape_warehouses(
                    city=city,
                    area_type="commercial",
                    min_area=min_area,
                    max_price=max_price
                )
                
                # Convert to warehouse models and add to results
                for data in results:
                    warehouse = scraper.to_warehouse_model(data)
                    if warehouse not in all_warehouses:  # Avoid duplicates
                        all_warehouses.append(warehouse)
        except Exception as e:
            print(f"Error performing real-time scraping: {str(e)}")
    
    # Filter warehouses based on criteria
    filtered_warehouses = all_warehouses
    
    if location:
        filtered_warehouses = [w for w in filtered_warehouses if location.lower() in w.location.lower()]
    
    if min_area:
        filtered_warehouses = [w for w in filtered_warehouses if w.area_sqft >= min_area]
    
    if max_price:
        filtered_warehouses = [w for w in filtered_warehouses if w.price_per_month <= max_price]
    
    if facilities:
        filtered_warehouses = [
            w for w in filtered_warehouses 
            if any(facility in [f.lower() for f in w.facilities] for facility in facilities)
        ]
    
    if availability and availability == "true":
        filtered_warehouses = [w for w in filtered_warehouses if w.availability]
    
    return templates.TemplateResponse(
        "warehouse_list.html", 
        {
            "request": request, 
            "warehouses": filtered_warehouses, 
            "current_user": request.state.current_user,
            "search_query": {
                "location": location,
                "min_area": min_area,
                "max_price": max_price
            }
        }
    )

# Remove public scraping endpoints
# The scraping functionality remains in the scraper module for internal use only 