import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/pollution.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    PROJECT_NAME: str = "CleanSignal"

settings = Settings()