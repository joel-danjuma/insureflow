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
    POSTGRES_PORT: str = "5432"
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
        return f"postgresql://{data.get('POSTGRES_USER', 'insureflow')}:{data.get('POSTGRES_PASSWORD', 'password')}@{data.get('POSTGRES_SERVER', 'localhost')}:{data.get('POSTGRES_PORT', '5432')}/{data.get('POSTGRES_DB', 'insureflow')}"
    
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
    
    # GAPS (GTBank Automated Payment System) Configuration
    GAPS_BASE_URL: str = "https://gtweb6.gtbank.com/GSTPS/GAPS_FileUploader/FileUploader.asmx"  # Test URL
    GAPS_CUSTOMER_ID: str = ""  # GAPS Access Code (encrypted)
    GAPS_USERNAME: str = ""  # GAPS Username (encrypted)
    GAPS_PASSWORD: str = ""  # GAPS Password (encrypted)
    GAPS_CHANNEL: str = "GSTP"  # Channel identifier
    GAPS_PUBLIC_KEY: str = """MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCrtPgIUBsQscypy+2A2l6oHKlLRTgD4hlrYKW9
IrAK4ll0FPndJ3i57CioPalYKdNMF9+K4mFaGfT3dAMRSgWWWDeaerHx35VLgdX/wFTN5Zf1QYGe
WiKyAmCAXoPwtlfvlLqsr9NMBJ3Ua+fFqSC4/6ThhudMlrxNL/ut/kd+pQIDAQAB"""  # Test public key
    
    # Settlement Configuration
    INSUREFLOW_SETTLEMENT_ACCOUNT: str = ""  # InsureFlow's settlement account number
    INSUREFLOW_COMMISSION_RATE: float = 0.75  # 0.75% commission rate
    HABARI_COMMISSION_RATE: float = 0.25  # 0.25% commission rate
    PLATFORM_COMMISSION_RATE: float = 1.0  # Total platform commission (0.75% + 0.25%)
    AUTO_SETTLEMENT_ENABLED: bool = True  # Enable automatic settlements
    SETTLEMENT_THRESHOLD: float = 10000.0  # Minimum amount for settlement (₦10,000)
    
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