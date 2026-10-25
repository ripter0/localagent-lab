from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reports = relationship("Report", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

class Report(Base):
    """Pollution report model."""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    location = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    pollutant_type = Column(String(100), default="")
    severity = Column(Integer, default=3)  # 1-5 scale
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    photo_url = Column(String(500), nullable=True)
    status = Column(String(20), default="pending")  # pending, verified, resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="reports")

    def __repr__(self):
        return f"<Report(id={self.id}, location='{self.location}', severity={self.severity})>"

class UrgentReport(Base):
    """Urgent report model for high-priority incidents."""
    __tablename__ = "urgent_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    urgency_level = Column(String(20), default="high")  # high, medium, low
    requires_immediate_action = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    report = relationship("Report", back_populates="urgent_report")

    def __repr__(self):
        return f"<UrgentReport(id={self.id}, urgency_level='{self.urgency_level}')>"

class Verification(Base):
    """Verification model for admin verification of reports."""
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    verified_by = Column(String(100), nullable=False)  # admin username
    verification_status = Column(String(20), default="pending")  # pending, verified, rejected
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    report = relationship("Report", back_populates="verification")

    def __repr__(self):
        return f"<Verification(id={self.id}, status='{self.verification_status}')>"
