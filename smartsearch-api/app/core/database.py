"""
Database connection and session management for SmartSearch API.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import redis

from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

# Connections are tested by startup/readiness, not during module import.
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db() -> Session:
    """
    Dependency to get DB session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """
    Dependency to get Redis client.
    """
    return redis_client

def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)
