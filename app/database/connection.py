"""
================================================================================
🎯 DATA ACCESS LAYER: DATABASE ENGINE & SESSION MANAGER
================================================================================
Description:
  This core module manages the connection lifecycle for the PostgreSQL cloud
  instance. It dynamically builds connection URIs, corrects dialect string 
  prefixes, and configures connection pooling factories to establish stable,
  reusable session links.
================================================================================
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    unified_url = os.getenv("DATABASE_URL")
    if unified_url:
        # Enforce SQLAlchemy dialect prefix compatibility
        if unified_url.startswith("postgres://"):
            unified_url = unified_url.replace("postgres://", "postgresql://", 1)
        return unified_url

    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres") 
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "ai_news_aggregator")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


# Configured with pool_pre_ping to automatically detect and discard dropped connections
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    return SessionLocal()