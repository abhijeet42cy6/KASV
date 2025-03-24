from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from fastapi.responses import RedirectResponse
from functools import wraps

# Security configuration
SECRET_KEY = "your-secret-key-keep-it-secret"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Login required decorator function for protecting routes
def login_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        print(f"[DEBUG] login_required decorator called for {func.__name__}")
        
        # Extract request from kwargs or args
        request = kwargs.get('request')
        if request is None:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    print(f"[DEBUG] Found request in args")
                    break
        
        # If no request found, this is unexpected but try to proceed
        if request is None:
            print(f"[DEBUG] No request found in {func.__name__} - unexpected error")
            return await func(*args, **kwargs)
        
        # Check if user is authenticated
        is_authenticated = hasattr(request.state, "current_user") and request.state.current_user is not None
        print(f"[DEBUG] User authenticated: {is_authenticated}")
        
        if is_authenticated:
            print(f"[DEBUG] User: {request.state.current_user.username}")
            # User is authenticated, call the original function with original args
            return await func(*args, **kwargs)
        else:
            # User is not authenticated, redirect to login
            redirect_url = f"/auth/login?next={request.url.path}"
            print(f"[DEBUG] Redirecting to: {redirect_url}")
            return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    
    return wrapper

def verify_admin(user: User = Depends(get_current_active_user)):
    """Check if the user is an admin"""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user

def verify_owner(user: User = Depends(get_current_active_user)):
    if user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only warehouse owners can perform this action"
        )
    return user 