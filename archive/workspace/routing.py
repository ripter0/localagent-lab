from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from model_config import User, Location, PollutionReport
from config import settings
from datetime import datetime
import os

router = APIRouter(prefix="/api", tags=["pollution"])

def get_db():
    """Get database session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(settings.DATABASE_URL.replace("sqlite:///./", "sqlite:///:memory:"))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/reports", response_model=list[dict])
def get_reports(db: Session = Depends(get_db), limit: int = 10, offset: int = 0):
    """Get recent pollution reports"""
    reports = db.query(PollutionReport).order_by(PollutionReport.reported_at.desc()).limit(limit).offset(offset).all()
    return [{
        "id": r.id,
        "pollutant_type": r.pollutant_type,
        "severity": r.severity,
        "description": r.description,
        "status": r.status,
        "reported_at": r.reported_at.isoformat(),
        "location_name": r.location.name if r.location else None
    } for r in reports]

@router.get("/reports/{report_id}", response_model=dict)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get single pollution report"""
    report = db.query(PollutionReport).filter(PollutionReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "id": report.id,
        "pollutant_type": report.pollutant_type,
        "severity": report.severity,
        "description": report.description,
        "status": report.status,
        "reported_at": report.reported_at.isoformat(),
        "location_name": report.location.name if report.location else None
    }

@router.post("/reports", status_code=status.HTTP_201_CREATED)
def create_report(report_data: dict, db: Session = Depends(get_db)):
    """Create new pollution report"""
    location = db.query(Location).first()
    if not location:
        raise HTTPException(status_code=404, detail="No locations available")
    
    new_report = PollutionReport(
        user_id=1,
        location_id=location.id,
        pollutant_type=report_data.get("pollutant_type", "unknown"),
        severity=report_data.get("severity", 3),
        description=report_data.get("description", ""),
        photo_url=report_data.get("photo_url")
    )
    db.add(new_report)
    db.commit()
    return {"message": "Report submitted successfully", "id": new_report.id}

@router.get("/locations", response_model=list[dict])
def get_locations(db: Session = Depends(get_db)):
    """Get all locations"""
    locations = db.query(Location).all()
    return [{"id": l.id, "name": l.name, "latitude": l.latitude, "longitude": l.longitude} for l in locations]

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get pollution statistics"""
    total_reports = db.query(func.count(PollutionReport.id)).scalar()
    pending_reports = db.query(func.count(PollutionReport.id)).filter(PollutionReport.status == "pending").scalar()
    return {"total_reports": total_reports, "pending_reports": pending_reports}