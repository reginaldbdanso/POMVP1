from sqlalchemy import create_engine, text  # Add text import
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# Add debug logging for environment variables
logger.info("Checking environment variables...")
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    missing = [
        var for var, val in {
            "DB_USER": DB_USER,
            "DB_PASSWORD": DB_PASSWORD,
            "DB_HOST": DB_HOST,
            "DB_NAME": DB_NAME
        }.items() if not val
    ]
    logger.error(f"Missing environment variables: {', '.join(missing)}")
    raise ValueError("Missing required environment variables")

# Construct Database URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
logger.info(f"Attempting to connect with user '{DB_USER}' to host '{DB_HOST}'")

# After constructing DATABASE_URL, add:
logger.info(f"Attempting to connect to MySQL at: {DB_HOST}")

try:
    # Create SQLAlchemy engine with connection pool settings
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800
    )
    
    # Test the connection using text()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        logger.info("Successfully connected to MySQL database")
        
except SQLAlchemyError as e:
    logger.error(f"Database connection error: {str(e)}")
    raise

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