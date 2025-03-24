from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
import re


class OwnerInfo(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str
    email: EmailStr
    company: Optional[str] = Field(None, max_length=100)
    gst_number: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        # More flexible Indian phone number validation that accepts various formats
        # Accepts:
        # - +91 followed by 10 digits starting with 6-9
        # - 91 followed by 10 digits starting with 6-9
        # - Just 10 digits starting with 6-9
        # With or without spaces, dashes, etc.
        
        # First, clean the number by removing spaces, dashes, etc.
        cleaned = re.sub(r'[^0-9+]', '', v)
        
        # Check for various valid formats
        if re.match(r'^\+?91[6-9]\d{9}$', cleaned) or re.match(r'^[6-9]\d{9}$', cleaned):
            return v
        
        raise ValueError('Invalid Indian phone number format')
    
    @validator('gst_number')
    def validate_gst(cls, v):
        if v:
            # GST number validation (15 characters, starts with 2 digits)
            if not re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', v):
                raise ValueError('Invalid GST number format')
        return v
    
    model_config = {
        "extra": "forbid"
    }

class Warehouse(BaseModel):
    """
    Warehouse data model for storing warehouse listings
    """
    id: Optional[int] = None
    title: str = Field(..., min_length=5, max_length=200)
    location: str = Field(..., min_length=5, max_length=200)
    area_sqft: int = Field(..., gt=0, lt=1000000)  # Reasonable limits for warehouse size
    price_per_month: float = Field(..., gt=0, lt=10000000)  # Reasonable limits for price
    facilities: List[str]
    owner_info: OwnerInfo
    description: str = Field(..., min_length=50, max_length=2000)
    availability: bool = True
    verified: bool = False
    source: Optional[str] = None
    creator_username: Optional[str] = None
    
    @validator('facilities')
    def validate_facilities(cls, v):
        # Clean and validate facilities list
        cleaned = [f.strip() for f in v if f.strip()]
        if not cleaned:
            raise ValueError('At least one facility is required')
        return cleaned
    
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
                    "phone": "+91 9876543210",
                    "email": "john@example.com"
                },
                "description": "Spacious warehouse ideal for bulk storage"
            }
        }
    } 