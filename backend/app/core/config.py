import secrets
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    
    # Database configuration
    DATABASE_URL: str = "postgresql://forest_user:forest_password@localhost:5432/forest_carbon_db"
    TEST_DATABASE_URL: Optional[str] = None
    
    # JWT configuration
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Development mode configuration
    DEVELOPMENT_MODE: bool = True
    
    # Auth0 configuration
    AUTH0_DOMAIN: Optional[str] = None
    AUTH0_API_AUDIENCE: Optional[str] = None
    AUTH0_ISSUER: Optional[str] = None
    AUTH0_ALGORITHMS: str = "RS256"

    # Stripe configuration (optional for development)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_API_VERSION: str = "2022-11-15"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 