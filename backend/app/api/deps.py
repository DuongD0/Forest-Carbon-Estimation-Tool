from typing import Generator, Optional, Any
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import SecurityScopes, OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app import crud, models, schemas
from app.core.security import auth
from app.core.auth import Auth0
from app.db.session import SessionLocal

# This is a placeholder for the real Auth0 flow. In a real application,
# the token URL would be on the Auth0 domain.
# For API validation, we only care about the token itself.
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{auth.domain}/authorize",
    tokenUrl=f"https://{auth.domain}/oauth/token",
)

auth = Auth0() 
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
    try:
        payload = auth.verify_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = crud.user.get_by_auth0_id(db, auth0_id=payload['sub'])
    if not user:
        # User doesn't exist, create a new one (JIT Provisioning)
        user_in = schemas.UserCreate(
            auth0_id=payload['sub'],
            email=payload.get('email'),
            name=payload.get('name', payload.get('nickname')),
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