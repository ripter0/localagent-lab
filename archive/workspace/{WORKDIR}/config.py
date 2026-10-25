import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings for CleanSignal."""
    
    # Application
    APP_NAME: str = "CleanSignal"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # Database (SQLite for dev, PostgreSQL for production)
    DATABASE_URL: str = "sqlite:///./data/cleansignal.db"
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS Configuration
    CORS_ORIGINS: list = ["*"]
    
    # JWT Secret Key (use strong key in production)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email Settings (for notifications)
    EMAIL_SERVER: str = os.getenv("EMAIL_SERVER", "")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    
    # File Upload
    UPLOAD_DIR: str = "data/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = ["png", "jpg", "jpeg", "gif"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()