"""
Security utilities for SmartSearch API.
"""

import hashlib
import hmac
import uuid
from datetime import UTC, datetime, timedelta
from typing import Optional
import jwt
from jwt import PyJWTError
import bcrypt
_orig_hashpw = bcrypt.hashpw
_orig_checkpw = bcrypt.checkpw
bcrypt.hashpw = lambda password, salt: _orig_hashpw(password[:72] if len(password) > 72 else password, salt)
bcrypt.checkpw = lambda password, hashed_password: _orig_checkpw(password[:72] if len(password) > 72 else password, hashed_password)
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Header, Query
from fastapi.security import HTTPBearer
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.database import APIKey, Product, Store, User

# Security settings
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token scheme
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    now = datetime.now(UTC)
    to_encode.update({
        "exp": expire,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token.credentials,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_owned_store(db: Session, store_id: str, user_id: str) -> Store:
    """Return a store only when it belongs to the authenticated user."""
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.owner_user_id == user_id,
    ).first()
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    return store


def get_owned_product(db: Session, product_id: str, user_id: str) -> Product:
    """Return a product only when its store belongs to the authenticated user."""
    product = db.query(Product).join(Store).filter(
        or_(Product.id == product_id, Product.external_id == product_id),
        Store.owner_user_id == user_id,
    ).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def hash_api_key(api_key: str) -> str:
    """Hash a high-entropy API key for deterministic lookup."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def api_key_prefix(api_key: str) -> str:
    return api_key[:16]


def api_key_has_scope(db_api_key: APIKey, required_scope: str) -> bool:
    scopes = {scope.strip() for scope in (db_api_key.scopes or "").split(",")}
    return required_scope in scopes


def require_api_key_scope(db_api_key: APIKey, required_scope: str) -> None:
    if not api_key_has_scope(db_api_key, required_scope):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"API key lacks required '{required_scope}' scope",
        )

def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key_header: Optional[str] = Header(None, alias="api_key"),
    api_key_query: Optional[str] = Query(None, alias="api_key"),
    db: Session = Depends(get_db)
):
    """Verify API key and return associated store."""
    api_key = x_api_key or api_key_header or api_key_query
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    supplied_hash = hash_api_key(api_key)
    db_api_key = db.query(APIKey).filter(
        APIKey.key_hash == supplied_hash,
        APIKey.is_active == True,
        APIKey.revoked_at.is_(None),
    ).first()

    # Temporary compatibility for pre-migration test/seed data only.
    if db_api_key is None:
        legacy_key = db.query(APIKey).filter(
            APIKey.key == api_key,
            APIKey.is_active == True,
            APIKey.revoked_at.is_(None),
        ).first()
        if legacy_key and hmac.compare_digest(legacy_key.key, api_key):
            db_api_key = legacy_key

    if db_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    now = datetime.now(UTC)
    if db_api_key.expires_at is not None:
        expires_at = db_api_key.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired",
            )

    # Check if associated store is active
    store = db.query(Store).filter(
        Store.id == db_api_key.store_id,
        Store.is_active == True
    ).first()

    if store is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Associated store is inactive",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Update last used timestamp
    db_api_key.last_used_at = now
    db.commit()

    return db_api_key, store

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate a user with email and password."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not user.password_hash:
        return False
    # Verify password
    if not pwd_context.verify(password, user.password_hash):
        return False
    return user
