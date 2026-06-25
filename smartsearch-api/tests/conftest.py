"""
Pytest configuration and fixtures for testing.
"""

import bcrypt
_orig_hashpw = bcrypt.hashpw
_orig_checkpw = bcrypt.checkpw
bcrypt.hashpw = lambda password, salt: _orig_hashpw(password[:72] if len(password) > 72 else password, salt)
bcrypt.checkpw = lambda password, hashed_password: _orig_checkpw(password[:72] if len(password) > 72 else password, hashed_password)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redirect SessionLocal to TestingSessionLocal for background tasks / app operations during testing
import app.core.database
app.core.database.SessionLocal = TestingSessionLocal



@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create the tables
    Base.metadata.create_all(bind=engine)

    # Create a new session for the test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)