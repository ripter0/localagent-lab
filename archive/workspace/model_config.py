from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model for citizen reporters"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    reports_count = Column(Integer, default=0)

class Location(Base):
    """Location model for pollution hotspots"""
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PollutionReport(Base):
    """Pollution report model for citizen submissions"""
    __tablename__ = "pollution_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    pollutant_type = Column(String(50), nullable=False)  # smoke, water, noise, etc.
    severity = Column(Integer, nullable=False)  # 1-5 scale
    description = Column(Text, nullable=True)
    photo_url = Column(String(255), nullable=True)
    status = Column(String(20), default="pending")  # pending, verified, resolved
    reported_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reports_count")
    location = relationship("Location")