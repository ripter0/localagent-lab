from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
import api

# Create FastAPI app
app = FastAPI(
    title="CleanSignal API",
    description="Citizen pollution reporting platform",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup (SQLite for development, PostgreSQL for production)
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Include API routes from api.py
from api import app as api_app
app.include_router(api_app.routes)

@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "name": "CleanSignal",
        "description": "Citizen pollution reporting platform",
        "version": "1.0.0",
        "endpoints": [
            "/api/register - Register new user",
            "/api/login - Login and get token",
            "/api/reports - Submit pollution report",
            "/api/reports - Get all reports",
            "/api/reports/search/{location} - Search by location",
            "/api/reports/urgent - Get urgent reports"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "database": "connected"}

# Initialize database tables (for SQLite, this creates the file)
def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    # Create data directory if it doesn't exist
    import os
    os.makedirs("data", exist_ok=True)
    init_db()
    
    uvicorn.run(
        "app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )