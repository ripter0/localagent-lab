from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class PollutionReport(Base):
    __tablename__ = "pollution_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(255), nullable=False)
    pollutant_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Integer, default=1)  # 1-5 scale
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pending")
    verified_by = Column(String(255), nullable=True)
    verification_date = Column(DateTime, nullable=True)