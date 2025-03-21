import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from .routers import warehouse, auth, scraping
from .database import get_db
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
import logging

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create static directory if it doesn't exist
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
    os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

app = FastAPI(title="Warewolf", description="Warehouse broker platform")

# Templates configuration
templates = Jinja2Templates(directory="app/templates")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware to add current_user to request state
class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Get DB session
            db = next(get_db())
            
            # Check for user in cookie
            current_user = await auth.get_current_user_from_cookie(request, db)
            
            # Add to request state
            request.state.current_user = current_user
            
            # Log authentication status
            if current_user:
                logger.info(f"User authenticated: {current_user.username}")
            else:
                logger.info("No user authenticated")
                
            # Process request
            response = await call_next(request)
            
            return response
        except Exception as e:
            logger.error(f"Error in authentication middleware: {str(e)}")
            # Continue with no user
            request.state.current_user = None
            return await call_next(request)

app.add_middleware(AuthenticationMiddleware)

# Custom middleware to process template responses
class TemplateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Only process HTML responses
        if hasattr(response, "body") and b"<!DOCTYPE html>" in response.body:
            # The response is probably HTML, make sure current_user is passed to the template
            # (This is a simplified approach - in a real app you'd update the template engine)
            pass
            
        return response

app.add_middleware(TemplateMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(warehouse.router)
app.include_router(scraping.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "current_user": request.state.current_user})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 