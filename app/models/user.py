from sqlalchemy import Boolean, Column, Integer, String, Enum
from ..database import Base
import enum
from datetime import datetime
from sqlalchemy import DateTime

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OWNER = "owner"
    SEEKER = "seeker"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    phone = Column(String)
    company_name = Column(String, nullable=True)
    gst_number = Column(String, nullable=True)

    # For warehouse owners
    business_address = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    
    # For verification
    verification_token = Column(String, nullable=True)
    reset_password_token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True) 