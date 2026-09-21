"""
API routes for authentication.
"""

from datetime import timedelta
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.utils.security import (
    authenticate_user, create_access_token, get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.database import User
from app.models.schemas import AccountDeleteRequest, UserCreate, UserResponse, Token
from app.services.store_service import delete_store, get_stores
from app.services.user_service import create_user, delete_user, get_user_by_email
from app.core.database import get_db
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    if settings.BETA_INVITE_CODE and not (
        user.invite_code
        and secrets.compare_digest(user.invite_code, settings.BETA_INVITE_CODE)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A valid beta invitation is required",
        )

    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return create_user(db=db, user=user)

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login, get an access token for future requests."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.delete("/me")
def delete_current_user(
    confirmation: AccountDeleteRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Permanently delete the authenticated merchant and all owned store data."""
    if not authenticate_user(db, current_user.email, confirmation.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password confirmation failed",
        )

    owned_stores = get_stores(db, limit=10_000, owner_user_id=current_user.id)
    search_engine = request.app.state.search_engine
    for store in owned_stores:
        search_engine.delete_store_index(store.id)
        delete_store(db, store.id)

    delete_user(db, current_user.id)
    return {"message": "Account and owned store data deleted successfully"}
