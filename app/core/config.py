"""
Configuration settings for InsureFlow application.
"""
from pydantic import AnyHttpUrl, EmailStr
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "InsureFlow"
    API_V1_STR: str = "/api/v1"

    # Database settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[str] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> Optional[str]:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

    # JWT settings
    SECRET_KEY: str = "your-secret-key"
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

    class Config:
        case_sensitive = True
        env_file = ".env"


# Global settings instance
settings = Settings() 