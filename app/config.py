# app/config.py

from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str 
    APP_DESCRIPTION: str
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # Default to 'development'
    DEBUG: bool = ENVIRONMENT == "development"

    DATABASE_URL: str

    # JWT and authentication settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "myjwtsecretkey")  # Default secret

    # Celery Configuration
    CELERY_BROKER_URL: str 
    CELERY_RESULT_BACKEND: str 

    # Other security settings
    ALLOWED_HOSTS: list = ["*"]
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]  # Add frontend URL if applicable

    class Config:
        env_file=".env"

# Instantiate settings
settings = Settings()
