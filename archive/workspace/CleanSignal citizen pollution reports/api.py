from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from model_config import Base, PollutionReport
from config import settings
from typing import List, Optional
import json

app = FastAPI(title=settings.PROJECT_NAME)

def get_db():
    """Database session generator"""
    from sqlalchemy import create_engine
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    return SessionLocal()

class SessionLocal:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(bind=self.engine)
    
    def __enter__(self):
        return Session(self.engine)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

@app.get("/")
def read_root():
    """Root endpoint with API info"""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "description": "Citizen pollution reporting web application",
        "endpoints": ["/reports", "/reports/{report_id}", "/reports/search"]
    }

@app.get("/reports", response_model=List[dict])
def list_reports(skip: int = 0, limit: int = 10):
    """List all pollution reports"""
    with get_db() as db:
        reports = db.query(PollutionReport).offset(skip).limit(limit).all()
        return [{"id": r.id, "location": r.location, "pollutant_type": r.pollutant_type, 
                 "description": r.description, "severity": r.severity, "status": r.status} for r in reports]

@app.get("/reports/{report_id}")
def get_report(report_id: int):
    """Get a specific pollution report"""
    with get_db() as db:
        report = db.query(PollutionReport).filter(PollutionReport.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return {"id": report.id, "location": report.location, "pollutant_type": report.pollutant_type,
                "description": report.description, "severity": report.severity, "status": report.status}

@app.post("/reports", response_model=dict)
def create_report(report_data: dict):
    """Create a new pollution report"""
    with get_db() as db:
        report = PollutionReport(
            location=report_data.get('location'),
            pollutant_type=report_data.get('pollutant_type'),
            description=report_data.get('description'),
            severity=report_data.get('severity', 1)
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return {"id": report.id, "message": "Report created successfully"}

@app.delete("/reports/{report_id}")
def delete_report(report_id: int):
    """Delete a pollution report"""
    with get_db() as db:
        report = db.query(PollutionReport).filter(PollutionReport.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        db.delete(report)
        db.commit()
        return {"message": "Report deleted successfully"}

@app.get("/reports/search")
def search_reports(query: str):
    """Search pollution reports by location or pollutant type"""
    with get_db() as db:
        reports = db.query(PollutionReport).filter(
            PollutionReport.location.ilike(f'%{query}%') | 
            PollutionReport.pollutant_type.ilike(f'%{query}%')
        ).all()
        return [{"id": r.id, "location": r.location, "pollutant_type": r.pollutant_type,
                 "description": r.description} for r in reports]

@app.get("/reports/{report_id}/route")
def route_report(report_id: int):
    """Get AI-powered routing recommendation for a report"""
    from routing import RoutingEngine
    with get_db() as db:
        report = db.query(PollutionReport).filter(PollutionReport.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        engine = RoutingEngine()
        routing_result = engine.route_report({
            'location': report.location,
            'pollutant_type': report.pollutant_type,
            'description': report.description,
            'severity': report.severity
        })
        return routing_result