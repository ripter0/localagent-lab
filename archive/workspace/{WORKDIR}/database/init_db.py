"""
Database initialization script for CleanSignal.
Creates the SQLite database and all required tables.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Report, UrgentReport, Verification
from config import settings

def init_database():
    """Initialize the database with all tables."""
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully!")
    print(f"   Database location: {settings.DATABASE_URL}")
    
    return engine

def create_sample_data(engine):
    """Create sample data for testing (optional)."""
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Create a sample admin user
        from hashlib import sha256
        hashed_pw = sha256(b"admin123").hexdigest()
        
        admin_user = User(
            email="admin@cleansignal.com",
            username="admin",
            hashed_password=hashed_pw,
            is_active=1
        )
        session.add(admin_user)
        session.commit()
        print("✅ Sample admin user created!")
        
        # Create sample reports
        sample_reports = [
            Report(
                user_id=admin_user.id,
                location="Main Street, Downtown",
                description="Heavy smoke coming from factory chimney",
                pollutant_type="smoke",
                severity=4,
                status="pending"
            ),
            Report(
                user_id=admin_user.id,
                location="Riverside Park",
                description="Oil spill in the river near park entrance",
                pollutant_type="chemical",
                severity=5,
                status="pending"
            ),
            Report(
                user_id=admin_user.id,
                location="Industrial Zone B",
                description="Unusual green discharge from water treatment plant",
                pollutant_type="chemical",
                severity=3,
                status="verified"
            )
        ]
        
        for report in sample_reports:
            session.add(report)
        
        session.commit()
        print(f"✅ Created {len(sample_reports)} sample reports!")
        
    except Exception as e:
        session.rollback()
        print(f"⚠️  Error creating sample data: {e}")
    finally:
        session.close()

def main():
    """Main function to initialize database."""
    engine = init_database()
    
    # Ask user if they want sample data
    print("\nWould you like to create sample data? (y/n)")
    response = input().strip().lower()
    
    if response in ['y', 'yes']:
        create_sample_data(engine)
    else:
        print("✅ Database ready for use!")

if __name__ == "__main__":
    main()