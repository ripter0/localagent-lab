from fastapi import FastAPI
from config import settings
from api import app as api_app
from model_config import Base, PollutionReport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create database engine and session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Citizen pollution reporting web application",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "description": "CleanSignal - Citizen pollution reporting platform",
        "endpoints": [
            "/reports - List all reports",
            "/reports/{id} - Get specific report",
            "/reports - Create new report",
            "/reports/search - Search reports",
            "/reports/{id}/route - AI routing recommendation"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": settings.DATABASE_URL}

# Import API routes
from api import list_reports, get_report, create_report, delete_report, search_reports, route_report

@app.get("/reports")
def list_all_reports():
    """List all pollution reports"""
    with SessionLocal() as session:
        reports = session.query(PollutionReport).all()
        return [{"id": r.id, "location": r.location, "pollutant_type": r.pollutant_type,
                 "description": r.description, "severity": r.severity, "status": r.status} for r in reports]

@app.get("/reports/{report_id}")
def get_single_report(report_id: int):
    """Get a specific pollution report by ID"""
    with SessionLocal() as session:
        report = session.query(PollutionReport).filter(PollutionReport.id == report_id).first()
        if not report:
            return {"error": "Report not found"}
        return {"id": report.id, "location": report.location, "pollutant_type": report.pollutant_type,
                "description": report.description, "severity": report.severity, "status": report.status}

@app.post("/reports")
def create_new_report(report_data: dict):
    """Create a new pollution report"""
    with SessionLocal() as session:
        report = PollutionReport(
            location=report_data.get('location'),
            pollutant_type=report_data.get('pollutant_type'),
            description=report_data.get('description'),
            severity=report_data.get('severity', 1)
        )
        session.add(report)
        session.commit()
        session.refresh(report)
        return {"id": report.id, "message": "Report created successfully"}

@app.delete("/reports/{report_id}")
def delete_report_endpoint(report_id: int):
    """Delete a pollution report"""
    with SessionLocal() as session:
        report = session.query(PollutionReport).filter(PollutionReport.id == report_id).first()
        if not report:
            return {"error": "Report not found"}
        session.delete(report)
        session.commit()
        return {"message": "Report deleted successfully"}

@app.get("/reports/search")
def search_reports_endpoint(query: str):
    """Search pollution reports by location or pollutant type"""
    with SessionLocal() as session:
        reports = session.query(PollutionReport).filter(
            PollutionReport.location.ilike(f'%{query}%') | 
            PollutionReport.pollutant_type.ilike(f'%{query}%')
        ).all()
        return [{"id": r.id, "location": r.location, "pollutant_type": r.pollutant_type,
                 "description": r.description} for r in reports]

@app.get("/reports/{report_id}/route")
def get_routing_recommendation(report_id: int):
    """Get AI-powered routing recommendation for a report"""
    from routing import RoutingEngine
    with SessionLocal() as session:
        report = session.query(PollutionReport).filter(PollutionReport.id == report_id).first()
        if not report:
            return {"error": "Report not found"}
        
        engine = RoutingEngine()
        routing_result = engine.route_report({
            'location': report.location,
            'pollutant_type': report.pollutant_type,
            'description': report.description,
            'severity': report.severity
        })
        return routing_result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)