"""
Configuration settings for InsureFlow application.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database settings
    DATABASE_URL: str = "postgresql://insureflow:insureflow@localhost:5433/insureflow"
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT settings
    JWT_SECRET_KEY: str = "your_super_secret_jwt_key_here_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Squad Co Payment Gateway settings
    SQUAD_SECRET_KEY: Optional[str] = None
    SQUAD_PUBLIC_KEY: Optional[str] = None
    SQUAD_WEBHOOK_URL: Optional[str] = None
    SQUAD_BASE_URL: str = "https://api-d.squadco.com"
    
    # Application settings
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # CORS settings
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8501"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings() 