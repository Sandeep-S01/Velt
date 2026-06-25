"""
User service for handling user-related operations.
"""

from sqlalchemy.orm import Session
import bcrypt
_orig_hashpw = bcrypt.hashpw
_orig_checkpw = bcrypt.checkpw
bcrypt.hashpw = lambda password, salt: _orig_hashpw(password[:72] if len(password) > 72 else password, salt)
bcrypt.checkpw = lambda password, hashed_password: _orig_checkpw(password[:72] if len(password) > 72 else password, hashed_password)
from passlib.context import CryptContext
from app.models.database import User
from app.models.schemas import UserCreate, UserUpdate

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: str):
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get multiple users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    """Create a new user."""
    # Hash the password
    hashed_password = pwd_context.hash(user.password)

    # Create user dict without password field
    user_data = user.dict()
    del user_data['password']

    # Create user instance
    db_user = User(**user_data, password_hash=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: str, user: UserUpdate):
    """Update an existing user."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        update_data = user.dict(exclude_unset=True)
        # Hash password if it's being updated
        if 'password' in update_data:
            update_data['password_hash'] = pwd_context.hash(update_data.pop('password'))
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: str):
    """Delete a user."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate a user with email and password."""
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not pwd_context.verify(password, user.password_hash):
        return False
    return user