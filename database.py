from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Define Database URL (SQLite for now)
DATABASE_URL = "sqlite:///./events.db"

# Create Database Engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for defining models
Base = declarative_base()
