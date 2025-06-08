import secrets
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    
    # Auth0 settings
    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str
    AUTH0_ISSUER: str
    AUTH0_ALGORITHMS: str = "RS256"

    # Stripe settings
    STRIPE_SECRET_KEY: str
    STRIPE_API_VERSION: str = "2022-11-15"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 