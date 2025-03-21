import uvicorn
from app.database import Base, engine
# Import all models to ensure they're registered with SQLAlchemy
from app.models.user import User
from app.models.warehouse import Warehouse

print("Creating database tables...")
# Create database tables
Base.metadata.create_all(bind=engine)
print("Database tables created successfully")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 