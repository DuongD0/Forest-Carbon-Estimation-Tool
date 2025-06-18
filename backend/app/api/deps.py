from typing import Generator, Optional, Any
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import SecurityScopes, OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app import crud, models, schemas
from app.core.security import auth, Auth0
from app.db.session import SessionLocal

# This is a placeholder for the real Auth0 flow. In a real application,
# the token URL would be on the Auth0 domain.
# For API validation, we only care about the token itself.
auth = Auth0()

# Create OAuth2 scheme - use placeholder URLs if Auth0 is not configured
if auth.domain and auth.domain != "your_auth0_domain.auth0.com":
    oauth2_scheme = OAuth2AuthorizationCodeBearer(
        authorizationUrl=f"https://{auth.domain}/authorize",
        tokenUrl=f"https://{auth.domain}/oauth/token",
    )
else:
    # Use placeholder URLs for development
    oauth2_scheme = OAuth2AuthorizationCodeBearer(
        authorizationUrl="https://placeholder.auth0.com/authorize",
        tokenUrl="https://placeholder.auth0.com/oauth/token",
    )

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/login/access-token"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_current_user(
    security_scopes: SecurityScopes, 
    db: Session = Depends(get_db), 
    token: str = Security(reusable_oauth2)
) -> models.User:
    from app.core.config import settings
    
    # For development mode, accept dev token and create/return a test user
    if settings.DEVELOPMENT_MODE and token == "dev-token-123":
        # Development mode - create/return a test user
        test_user = crud.user.get_by_email(db, email="test@example.com")
        if not test_user:
            user_in = schemas.UserCreate(
                email="test@example.com",
                first_name="Test",
                last_name="User",
                organization="Test Organization"
            )
            test_user = crud.user.create(db, obj_in=user_in)
        return test_user
    
    try:
        payload = await auth.verify_token(token, security_scopes)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = crud.user.get_by_email(db, email=payload.get('email'))
    if not user:
        # User doesn't exist, create a new one (JIT Provisioning)
        user_in = schemas.UserCreate(
            email=payload.get('email'),
            first_name=payload.get('given_name', ''),
            last_name=payload.get('family_name', ''),
            organization=payload.get('organization', '')
        )
        user = crud.user.create(db, obj_in=user_in)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_user(
    current_user: models.User = Security(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(
    current_user: models.User = Security(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user 