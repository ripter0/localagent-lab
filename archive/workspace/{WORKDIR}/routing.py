"""
Routing module for CleanSignal API.
Integrates all endpoints with FastAPI router and configures middleware.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api import app as api_app
from models import Base
from sqlalchemy import create_engine
from config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_application():
    """Create and configure the FastAPI application."""
    
    # Create main FastAPI app
    main_app = FastAPI(
        title=settings.APP_NAME,
        description="CleanSignal - Citizen Pollution Reporting System",
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS middleware
    main_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request logging middleware
    @main_app.middleware("*")
    async def log_requests(request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response
    
    # Include API routes from api.py
    main_app.include_router(
        api_app,
        prefix="/api",
        tags=["reports", "users", "admin"]
    )
    
    # Health check endpoint at root
    @main_app.get("/")
    async def root():
        return {
            "message": "Welcome to CleanSignal API",
            "version": settings.VERSION,
            "docs": "/docs"
        }
    
    # Include static files
    main_app.mount("/static", api_app.static_files)
    
    return main_app

def initialize_database():
    """Initialize the database with all tables."""
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    return engine

def setup_application():
    """Complete application setup including database initialization."""
    # Initialize database
    engine = initialize_database()
    
    # Create application instance
    app = create_application()
    
    logger.info(f"CleanSignal API initialized on {settings.API_HOST}:{settings.API_PORT}")
    return app, engine

if __name__ == "__main__":
    app, _ = setup_application()
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)