"""
CleanSignal API Endpoints
Handles pollution report submission, retrieval, and user management.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from models import User, Report, UrgentReport, Verification
from config import settings
from datetime import datetime, timedelta
import jwt
from typing import List, Optional
import hashlib

app = FastAPI(
    title="CleanSignal API",
    description="Citizen pollution reporting system",
    version=settings.VERSION
)

# Database session dependency
def get_db():
    from sqlalchemy import create_engine
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    try:
        yield SessionLocal()
    finally:
        pass

# JWT token functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user.hashed_password != hashed_password:
        return False
    return user

def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenName="access_token")), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

OAuth2PasswordBearer = lambda tokenName="access_token": None  # Placeholder for OAuth2

# Report endpoints
@app.get("/api/reports", response_model=List[Report])
def get_reports(skip: int = 0, limit: int = 100, status: Optional[str] = None):
    """Get all pollution reports with optional filtering."""
    query = Report.query
    if status:
        query = query.filter(Report.status == status)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply skip and limit
    reports = query.offset(skip).limit(limit).all()
    
    return {"reports": [r.dict() for r in reports], "total": total, "skip": skip, "limit": limit}

@app.get("/api/reports/{report_id}", response_model=Report)
def get_report(report_id: int):
    """Get a specific report by ID."""
    report = Report.query.filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.dict()

@app.post("/api/reports", response_model=Report)
def create_report(report: dict, db: Session = Depends(get_db)):
    """Create a new pollution report."""
    # Validate required fields
    if not report.get("location") or not report.get("description"):
        raise HTTPException(status_code=400, detail="Location and description are required")
    
    # Create report with default values
    db_report = Report(
        user_id=1,  # In production, get from authenticated user
        location=report["location"],
        description=report["description"],
        pollutant_type=report.get("pollutant_type", ""),
        severity=report.get("severity", 3),
        latitude=report.get("latitude"),
        longitude=report.get("longitude"),
        photo_url=report.get("photo_url"),
        status=report.get("status", "pending")
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report.dict()

@app.put("/api/reports/{report_id}", response_model=Report)
def update_report(report_id: int, report_data: dict, db: Session = Depends(get_db)):
    """Update an existing report."""
    report = Report.query.filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Update allowed fields
    update_data = report_data.copy()
    for field in ["location", "description", "pollutant_type", "severity", "status"]:
        if field in update_data:
            setattr(report, field, update_data[field])
    
    db.commit()
    db.refresh(report)
    return report.dict()

@app.delete("/api/reports/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a report (admin only)."""
    report = Report.query.filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(report)
    db.commit()
    return {"message": "Report deleted successfully"}

# Urgent reports endpoints
@app.get("/api/reports/urgent", response_model=List[dict])
def get_urgent_reports():
    """Get all urgent/high-severity reports."""
    urgent = Report.query.filter(Report.severity >= 4).all()
    return [r.dict() for r in urgent]

# User authentication endpoints
@app.post("/api/login", response_model=dict)
def login(credentials: dict):
    """User login endpoint."""
    username = credentials.get("username")
    password = credentials.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    user = authenticate_user(None, username, password)  # Will need db session
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"username": user.username, "email": user.email}
    }

@app.get("/api/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return {
        "username": current_user.username,
        "email": current_user.email,
        "reports_count": len(current_user.reports)
    }

# Admin verification endpoints
@app.post("/api/reports/{report_id}/verify", response_model=Verification)
def verify_report(report_id: int, verification_data: dict, db: Session = Depends(get_db)):
    """Admin verification of a report."""
    report = Report.query.filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    verification = Verification(
        report_id=report_id,
        verified_by=verification_data.get("admin_username", "admin"),
        verification_status=verification_data.get("status", "verified"),
        notes=verification_data.get("notes", "")
    )
    
    db.add(verification)
    db.commit()
    db.refresh(verification)
    return verification.dict()

@app.get("/api/reports/{report_id}/verification")
def get_verification(report_id: int):
    """Get verification status of a report."""
    verification = Verification.query.filter(Verification.report_id == report_id).first()
    if not verification:
        raise HTTPException(status_code=404, detail="No verification found")
    return verification.dict()

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "CleanSignal API"}
