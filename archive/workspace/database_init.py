from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from model_config import Base, User, Location, PollutionReport
from config import settings

def init_db():
    """Initialize database with tables and sample data"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create sample data
    with engine.connect() as conn:
        # Insert sample locations
        conn.execute(
            Location.__table__.insert(),
            [
                {"name": "Downtown Park", "latitude": 40.7128, "longitude": -74.0060, "description": "Central park area"},
                {"name": "Industrial Zone A", "latitude": 40.7589, "longitude": -73.9851, "description": "Manufacturing district"},
                {"name": "Riverside Community", "latitude": 40.6892, "longitude": -74.0445, "description": "Waterfront residential area"}
            ]
        )
    
    print("Database initialized successfully!")
    print("Sample locations created.")

if __name__ == "__main__":
    init_db()