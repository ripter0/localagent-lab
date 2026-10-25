import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/cleansignal.db"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # API
    API_VERSION: str = "v1"
    PROJECT_NAME: str = "CleanSignal"
    DESCRIPTION: str = "Citizen Pollution Reporting Platform"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()