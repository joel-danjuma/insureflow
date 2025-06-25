"""
Configuration settings for InsureFlow application.
"""
from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "InsureFlow"
    API_V1_STR: str = "/api/v1"

    # App Environment settings
    APP_ENV: str = "development"
    APP_DEBUG: str = "true"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: str = "8000"
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "insureflow"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "insureflow"
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        if isinstance(v, str) and v:
            return v
        # Get values from the validator info
        data = info.data if hasattr(info, 'data') else {}
        return f"postgresql://{data.get('POSTGRES_USER', 'insureflow')}:{data.get('POSTGRES_PASSWORD', 'password')}@{data.get('POSTGRES_SERVER', 'localhost')}/{data.get('POSTGRES_DB', 'insureflow')}"
    
    @property
    def jwt_secret(self) -> str:
        """Get JWT secret key, preferring JWT_SECRET_KEY over SECRET_KEY"""
        return self.JWT_SECRET_KEY or self.SECRET_KEY

    # JWT settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_SECRET_KEY: Optional[str] = None  # Alternative JWT key name
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    JWT_ALGORITHM: str = "HS256"
    
    # Redis settings
    REDIS_URL: Optional[str] = None

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Squad Co Payment Gateway  
    SQUAD_SECRET_KEY: str = ""  # Will be read from environment
    SQUAD_PUBLIC_KEY: str = ""  # Will be read from environment
    SQUAD_BASE_URL: str = "https://sandbox-api-d.squadco.com"  # Default to sandbox
    SQUAD_WEBHOOK_URL: Optional[str] = None  # Webhook URL for Squad Co payments
    
    # API Keys for AI features
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "ignore"  # Allow extra fields from environment
    }


# Global settings instance
settings = Settings() 