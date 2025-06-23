"""
Configuration settings for InsureFlow application.
"""
from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "InsureFlow"
    API_V1_STR: str = "/api/v1"

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

    # JWT settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    JWT_ALGORITHM: str = "HS256"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Squad Co Payment Gateway
    SQUAD_SECRET_KEY: str = "test_secret_key"
    SQUAD_PUBLIC_KEY: str = "test_public_key"
    SQUAD_BASE_URL: str = "https://sandbox-api-d.squadco.com"
    
    # API Keys for AI features
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }


# Global settings instance
settings = Settings() 