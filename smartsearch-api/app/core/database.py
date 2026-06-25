"""
Database connection and session management for SmartSearch API.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import redis

# Load environment variables
load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://smartsearch:smartsearch_pass@localhost:5433/smartsearch"
)

# Redis URL from environment variable
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create SQLAlchemy engine with fallback to SQLite if connection fails
try:
    if "postgresql" in DATABASE_URL:
        # Test connection with a short timeout
        test_engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 2})
        with test_engine.connect() as conn:
            pass
        engine = test_engine
        print("Connected to PostgreSQL successfully.")
    else:
        engine = create_engine(DATABASE_URL)
except Exception as e:
    print(f"Warning: Could not connect to database at {DATABASE_URL}: {e}")
    print("Falling back to local SQLite database: sqlite:///./smartsearch.db")
    DATABASE_URL = "sqlite:///./smartsearch.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create Redis client
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    # Test connection
    redis_client.ping()
except Exception as e:
    print(f"Warning: Could not connect to Redis: {e}")
    redis_client = None

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