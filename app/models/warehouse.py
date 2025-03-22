from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class OwnerInfo(BaseModel):
    name: str
    phone: str
    email: EmailStr
    company: Optional[str] = None
    gst_number: Optional[str] = None

class Warehouse(BaseModel):
    """
    Warehouse data model for storing warehouse listings
    """
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
    source: Optional[str] = None  # To track if the warehouse was manually added or scraped
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Large Storage Space in Delhi",
                "location": "Delhi, Sector 5",
                "area_sqft": 5000,
                "price_per_month": 50000,
                "facilities": ["24/7 Security", "Loading Dock", "Climate Control"],
                "owner_info": {
                    "name": "John Doe",
                    "phone": "+91 1234567890",
                    "email": "john@example.com"
                },
                "description": "Spacious warehouse ideal for bulk storage"
            }
        }
    } 