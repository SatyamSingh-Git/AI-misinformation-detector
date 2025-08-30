from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings
# --- Database Configuration ---

# For a hackathon, SQLite is the easiest to set up.
# The database will be a single file named 'misinformation.db' in the backend's root directory.
SQLALCHEMY_DATABASE_URL = "sqlite:///./misinformation.db"

# If you were deploying to production, you would use PostgreSQL like this:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# --- SQLAlchemy Engine Setup ---
settings = get_settings()
# The engine is the central point of contact for the application to the database.
# The 'connect_args' are only needed for SQLite to allow multithreaded access.
engine = create_engine(settings.DATABASE_URL)

# --- Session Management ---

# A SessionLocal class is a factory for new database sessions.
# Each instance of SessionLocal will be a single database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Declarative Base ---

# We will inherit from this Base class to create each of the ORM models.
# It provides the basic functionality for our database models.
Base = declarative_base()

# --- Dependency for FastAPI ---
# This function will be used in our API routes to get a database session.
# It ensures that the database connection is always closed after a request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
