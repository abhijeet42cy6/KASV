from fastapi import APIRouter, HTTPException, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserRole
from ..auth.utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
    login_required
)
from datetime import timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
import logging

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = Jinja2Templates(directory="app/templates")

# Temporary user database for demonstration
users_db = {
    "demo_owner": {"username": "demo_owner", "password": "password", "role": "owner"},
    "demo_seeker": {"username": "demo_seeker", "password": "password", "role": "seeker"}
}

# User Create model for API
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    role: UserRole
    phone: str
    company_name: Optional[str] = None
    gst_number: Optional[str] = None
    business_address: Optional[str] = None
    business_type: Optional[str] = None
    
    model_config = {
        "extra": "forbid"
    }

class Token(BaseModel):
    access_token: str
    token_type: str
    
    model_config = {
        "extra": "forbid"
    }

@router.get("/login", response_class=HTMLResponse, name="login")
async def login_page(request: Request):
    logger.info("Login page requested")
    return templates.TemplateResponse("login.html", {"request": request, "current_user": request.state.current_user})

# Login endpoint for the form submission
@router.post("/login_form", name="login_form")
async def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Login attempt for user: {username}")
    print(f"[DEBUG] Login attempt for user: {username}")
    
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        logger.warning(f"Failed login attempt for user: {username}")
        print(f"[DEBUG] Failed login - invalid credentials for: {username}")
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid username or password", "current_user": None}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    logger.info(f"User {username} logged in successfully")
    print(f"[DEBUG] User {username} logged in successfully")
    
    # Store the token in a cookie and redirect to home
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True,
        max_age=1800,  # 30 minutes in seconds
        expires=1800,  # 30 minutes in seconds
        samesite="lax",  # Helps with CSRF protection
        secure=False  # Set to True in production with HTTPS
    )
    print(f"[DEBUG] Cookie set with token: Bearer {access_token[:10]}...")
    return response

@router.get("/register", response_class=HTMLResponse, name="register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "current_user": request.state.current_user})

# Post registration endpoint that accepts form data
@router.post("/register_form")
async def register_user_form(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    role: str = Form(...),
    phone: str = Form(...),
    company_name: Optional[str] = Form(None),
    gst_number: Optional[str] = Form(None),
    business_address: Optional[str] = Form(None),
    business_type: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Check if user already exists
    if db.query(User).filter(User.email == email).first():
        error_msg = "Email already registered"
        return templates.TemplateResponse("register.html", {"request": request, "error": error_msg, "current_user": None})
    
    if db.query(User).filter(User.username == username).first():
        error_msg = "Username already taken"
        return templates.TemplateResponse("register.html", {"request": request, "error": error_msg, "current_user": None})
    
    try:
        # Validate role
        user_role = UserRole(role)
    except ValueError:
        error_msg = "Invalid role"
        return templates.TemplateResponse("register.html", {"request": request, "error": error_msg, "current_user": None})
    
    # Create new user
    hashed_password = get_password_hash(password)
    db_user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=hashed_password,
        role=user_role,
        phone=phone,
        company_name=company_name,
        gst_number=gst_number,
        business_address=business_address,
        business_type=business_type
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"User {username} registered successfully")
    # Redirect to login page
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

# Token endpoint for API authentication
@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid username or password", "current_user": None}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Store the token in a cookie and redirect to home
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/logout", name="logout")
async def logout():
    logger.info("User logged out")
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

# Add a function to check if a user is authenticated from cookies
async def get_current_user_from_cookie(request: Request, db: Session):
    token = request.cookies.get("access_token")
    logger.info(f"Checking cookie for token: {'Found' if token else 'Not found'}")
    print(f"[DEBUG] get_current_user_from_cookie - token: {'Present' if token else 'None'}")
    
    if not token or not token.startswith("Bearer "):
        print(f"[DEBUG] Token invalid or missing Bearer prefix: {token}")
        return None
    
    token = token.replace("Bearer ", "")
    print(f"[DEBUG] Processing token (first 10 chars): {token[:10] if len(token) > 10 else token}")
    
    try:
        logger.info("Attempting to decode token")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        logger.info(f"Token decoded successfully, username: {username}")
        print(f"[DEBUG] Token decoded successfully for: {username}")
        
        if username is None:
            logger.warning("No username found in token")
            print("[DEBUG] No username found in token")
            return None
    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        print(f"[DEBUG] JWT decode error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}")
        print(f"[DEBUG] Unexpected token error: {str(e)}")
        return None
    
    user = db.query(User).filter(User.username == username).first()
    logger.info(f"User found: {'Yes' if user else 'No'}")
    print(f"[DEBUG] User found in database: {'Yes' if user else 'No'}")
    if user:
        print(f"[DEBUG] Username: {user.username}, Role: {user.role}")
    return user 

# Debug route to check auth status
@router.get("/debug-auth")
async def debug_auth(request: Request):
    """Debug endpoint to check auth status"""
    auth_status = {
        "has_current_user": hasattr(request.state, "current_user"),
        "current_user": None,
        "cookie_token": request.cookies.get("access_token", "No token"),
        "path": str(request.url)
    }
    
    if hasattr(request.state, "current_user") and request.state.current_user:
        auth_status["current_user"] = {
            "username": request.state.current_user.username,
            "role": str(request.state.current_user.role),
            "email": request.state.current_user.email
        }
    
    return auth_status 

# User profile page
@router.get("/profile", response_class=HTMLResponse, name="profile")
@login_required
async def profile(request: Request):
    """Display user profile page."""
    current_user = request.state.current_user
    return templates.TemplateResponse(
        "profile.html", 
        {"request": request, "current_user": current_user}
    ) 