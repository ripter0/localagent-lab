from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from model_config import Incident, Comment, Notification
from config import Config
import os

app = FastAPI(
    title=Config.APP_NAME,
    version=Config.APP_VERSION,
    description="Citizen pollution reporting web application"
)

def get_db():
    """Get database session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

@app.get("/")
def root():
    return {"message": "Welcome to CleanSignal - Pollution Reporting API", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "app": Config.APP_NAME, "version": Config.APP_VERSION}

@app.post("/api/incidents")
def create_incident(incident_data: dict):
    """Create new pollution incident report"""
    db = get_db()
    
    # Validate API key if needed
    api_key = os.getenv("API_KEY", "")
    if api_key and incident_data.get("api_key") != api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    new_incident = Incident(
        title=incident_data["title"],
        description=incident_data["description"],
        location_lat=incident_data.get("location_lat", 0),
        location_lon=incident_data.get("location_lon", 0),
        incident_type=incident_data.get("incident_type", "air_quality"),
        severity=incident_data.get("severity", 1),
        status=incident_data.get("status", "pending"),
        photos=incident_data.get("photos", None),
        reporter_name=incident_data.get("reporter_name", "Anonymous"),
        contact_email=incident_data.get("contact_email", None)
    )
    
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    
    # Create notification for admin
    if Config.NOTIFICATION_ENABLED:
        try:
            notification = Notification(
                incident_id=new_incident.id,
                message=f"New {new_incident.incident_type} reported: {new_incident.title}",
                is_admin=True
            )
            db.add(notification)
            db.commit()
        except Exception as e:
            print(f"Notification error: {e}")
    
    return new_incident

@app.get("/api/incidents")
def get_incidents(skip: int = 0, limit: int = 10):
    """Get list of incidents"""
    db = get_db()
    incidents = db.query(Incident).offset(skip).limit(limit).all()
    return [inc.to_dict() for inc in incidents]

@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: int):
    """Get single incident by ID"""
    db = get_db()
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident.to_dict()

@app.get("/api/incidents/pending")
def get_pending_incidents():
    """Get pending incidents for admin review"""
    db = get_db()
    incidents = db.query(Incident).filter(Incident.status == "pending").all()
    return [inc.to_dict() for inc in incidents]

@app.get("/api/incidents/verified")
def get_verified_incidents():
    """Get verified incidents"""
    db = get_db()
    incidents = db.query(Incident).filter(Incident.status == "verified").all()
    return [inc.to_dict() for inc in incidents]

@app.get("/api/incidents/resolved")
def get_resolved_incidents():
    """Get resolved incidents"""
    db = get_db()
    incidents = db.query(Incident).filter(Incident.status == "resolved").all()
    return [inc.to_dict() for inc in incidents]

@app.get("/api/incidents/{incident_id}/comments")
def get_incident_comments(incident_id: int):
    """Get comments for an incident"""
    db = get_db()
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    comments = db.query(Comment).filter(Comment.incident_id == incident_id).all()
    return [comment.to_dict() for comment in comments]

@app.post("/api/incidents/{incident_id}/comments")
def add_incident_comment(incident_id: int, comment_data: dict):
    """Add comment to an incident"""
    db = get_db()
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    new_comment = Comment(
        incident_id=incident_id,
        user_name=comment_data.get("user_name", "Anonymous"),
        message=comment_data["message"]
    )
    db.add(new_comment)
    db.commit()
    return new_comment.to_dict()

@app.post("/api/incidents/{incident_id}/status")
def update_incident_status(incident_id: int, status_data: dict):
    """Update incident status (admin only)"""
    db = get_db()
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Simple admin check - in production use JWT tokens
    if status_data.get("admin_key") != Config.ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    incident.status = status_data["status"]
    db.commit()
    return incident.to_dict()