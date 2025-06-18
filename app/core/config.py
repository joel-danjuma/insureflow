"""
Configuration settings for InsureFlow application.
"""
import os
from typing import Optional, List, AnyHttpUrl
from pydantic_settings import BaseSettings
from pydantic import EmailStr


class Settings(BaseSettings):
    """Application settings."""
    
    # Database settings
    DATABASE_URL: str
    
    # Redis settings
    REDIS_URL: str
    
    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # Squad Co Payment Gateway settings
    SQUAD_SECRET_KEY: str
    SQUAD_PUBLIC_KEY: str
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
    
    # Optional API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'  # Ignore extra variables from the env file
        case_sensitive = True


# Global settings instance
settings = Settings() 