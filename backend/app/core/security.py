from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
import os
from dotenv import load_dotenv
from app.core.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import SecurityScopes, OAuth2AuthorizationCodeBearer
import httpx
from jose import jwt, JWTError

load_dotenv()

# for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
# use .env for secrets
JWT_SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secure_default_secret_key_replace_it")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# for jwt tokens

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class Auth0:
    def __init__(self):
        self.domain = settings.AUTH0_DOMAIN
        self.audience = settings.AUTH0_API_AUDIENCE
        self.issuer = settings.AUTH0_ISSUER
        self.algorithms = [settings.AUTH0_ALGORITHMS]
        self.jwks_url = f"https://{self.domain}/.well-known/jwks.json" if self.domain else None

    async def get_jwks(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_url)
            response.raise_for_status()
            return response.json()

    async def verify_token(self, token: str, security_scopes: SecurityScopes):
        if token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication")

        # Skip Auth0 verification if domain is not properly configured (development mode)
        if not self.domain or self.domain == "your_auth0_domain.auth0.com":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Auth0 not configured - use development mode",
            )

        try:
            jwks = await self.get_jwks()
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"],
                    }
            if rsa_key:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=self.algorithms,
                    audience=self.audience,
                    issuer=self.issuer,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find appropriate key",
                )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
            ) from e

        if security_scopes.scopes:
            token_scopes = payload.get("scope", "").split()
            for scope in security_scopes.scopes:
                if scope not in token_scopes:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not enough permissions",
                    )
        
        return payload

auth = Auth0()

