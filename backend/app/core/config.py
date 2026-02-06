import os
import json
from typing import List, Optional, Dict, Any
from pydantic import Field, computed_field, validator, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
        env_file_encoding="utf-8",
        env_nested_delimiter="__"
    )

    # API configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "FineTuner"
    
    # CORS configuration - default origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://finetuner.io",
        "https://www.finetuner.io",
        "https://api.finetuner.io",
        "http://finetuner.io",
        "http://www.finetuner.io",
        "http://api.finetuner.io",
        "https://82.29.173.71:8000"
    ]
    
    # Additional CORS origins (for Railway or other deployments)
    ALLOWED_ORIGINS: Optional[str] = Field(default=None)
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, value, values):
        origins = []
        
        # Parse the main CORS origins
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        origins = [str(item) for item in parsed]
                except json.JSONDecodeError:
                    origins = [i.strip() for i in value.split(",")]
            else:
                origins = [i.strip() for i in value.split(",")]
        elif isinstance(value, list):
            origins = value
        
        # Add Railway domains pattern support
        # Railway uses *.up.railway.app format
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
        if allowed_origins:
            for origin in allowed_origins.split(","):
                origin = origin.strip()
                if origin and origin not in origins:
                    # Add both http and https variants
                    if not origin.startswith("http"):
                        origins.append(f"https://{origin}")
                        origins.append(f"http://{origin}")
                    else:
                        origins.append(origin)
        
        return origins
    
    # Security configuration
    SECRET_KEY: str = Field(default="your_secret_key_here")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=240)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # Database configuration
    # Railway provides DATABASE_URL directly, or use individual components
    DATABASE_URL: Optional[str] = Field(default=None)
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: str = Field(default="5432")
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="fintune")
    
    @computed_field
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Prefer DATABASE_URL if provided (Railway style)
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Otherwise construct from individual components
        if not all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_HOST, self.POSTGRES_DB]):
            return "postgresql://postgres:postgres@localhost/fintune"
        port = f":{self.POSTGRES_PORT}" if self.POSTGRES_PORT else ""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}{port}/{self.POSTGRES_DB}"
    
    # Stripe configuration
    STRIPE_SECRET_KEY: str = Field(default="")
    STRIPE_PUBLISHABLE_KEY: str = Field(default="")
    STRIPE_WEBHOOK_SECRET: str = Field(default="")
    
    # Stripe price IDs
    STRIPE_PRICE_STARTER: str = Field(default="")
    STRIPE_PRICE_PRO: str = Field(default="")
    STRIPE_PRICE_ENTERPRISE: str = Field(default="")
    STRIPE_PRICE_ID: str = Field(default="")  # Pour les achats de caractères
    
    # File storage configuration
    UPLOAD_DIR: str = Field(default="/tmp/uploads")
    MAX_UPLOAD_SIZE: int = Field(default=10485760)  # 10MB
    
    # Redis configuration
    REDIS_URL: str = Field(default="redis://redis:6379/0")

    # Debug mode
    DEBUG: bool = Field(default=False)

    # IA settings 
    OPENAI_API_KEY: str = Field(default="")
    ANTHROPIC_API_KEY: str = Field(default="")
    MISTRAL_API_KEY: str = Field(default="")
    
    # Content processing settings
    DEFAULT_AI_MODEL: str = Field(default="gpt-4.1")

    # Frontend configuration
    FRONTEND_URL: str = Field(default="https://finetuner.io")

    # Google OAuth configuration
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")
    GOOGLE_DISCOVERY_URL: str = Field(default="https://accounts.google.com/.well-known/openid-configuration")

    # Email configuration (NEW)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = Field(default=465) # Port SSL par défaut pour Hostinger
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_SENDER_EMAIL: EmailStr = Field(default="support@finetuner.io")
    SMTP_SENDER_NAME: str = Field(default="FineTuner")
    EMAIL_LOGO_URL: Optional[str] = None # URL publique du logo


settings = Settings() 