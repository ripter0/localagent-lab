from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user model."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """User creation model."""
    password: str

class UserUpdate(BaseModel):
    """User update model."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    """User response model with id and hashed password."""
    id: int
    is_active: bool
    created_at: datetime

class PollutionReport(BaseModel):
    """Pollution report model."""
    location: str
    description: str
    pollutant_type: Optional[str] = None  # smoke, water, noise, etc.
    severity: Optional[int] = None  # 1-5 scale
    timestamp: Optional[datetime] = None
    photo_url: Optional[str] = None
    reporter_id: Optional[int] = None