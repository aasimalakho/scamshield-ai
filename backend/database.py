"""
Database engine + session setup for ScamShield AI.

Uses SQLite for simplicity - zero setup, file-based, perfect for a
hackathon project and for running on a tablet/Colab/any machine with
no extra database server needed.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base

DATABASE_URL = "sqlite:///./scamshield.db"

# check_same_thread=False is needed only for SQLite, since FastAPI may
# use the connection across different threads.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session and closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
