from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Database URL - in production, use environment variables
# Default to SQLite if DATABASE_URL is not set
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Check if we can connect to PostgreSQL
    try:
        import psycopg2
        DATABASE_URL = "postgresql://postgres:postgres@localhost/fastapi_db"
        print("Using PostgreSQL database")
    except ImportError:
        # Fall back to SQLite
        DATABASE_URL = "sqlite:///./test.db"
        print("Using SQLite database")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={} if not DATABASE_URL.startswith("sqlite") else {"check_same_thread": False})

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()