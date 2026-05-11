""""This module is responsible for setting up the database connection 
and session management for the application. 
It defines the SQLAlchemy engine, session factory, 
and table registry that will be used throughout the app to interact with the database."""

from sqlalchemy import create_engine
from sqlalchemy.orm import registry, sessionmaker
from app.core.settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
table_registry = registry()
