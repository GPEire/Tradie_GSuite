"""
Application Configuration
Centralized configuration management
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "AI Email Extension API"
    app_version: str = "0.1.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    backend_host: str = os.getenv("BACKEND_HOST", "localhost")
    backend_port: int = int(os.getenv("BACKEND_PORT", 8000))
    
    # CORS
    allowed_origins: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,chrome-extension://*"
    ).split(",")
    
    # Google OAuth
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI", "")
    gmail_scopes: str = os.getenv(
        "GMAIL_SCOPES",
        "gmail.readonly,gmail.modify,gmail.labels"
    )
    
    # AI Services
    ai_provider: str = os.getenv("AI_PROVIDER", "openai")  # openai, anthropic, vertex
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")  # gpt-4, gpt-4-turbo, gpt-3.5-turbo
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./app.db"
    )
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "")
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "")
    
    # Frontend
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

