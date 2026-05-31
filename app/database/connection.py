import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load local environment parameters
load_dotenv()


def get_database_url() -> str:
    """
    Dynamically tracks down your Postgres database credentials.
    Prioritizes a single unified connection URL, falling back to 
    individual piece-by-piece environment blocks if running locally.
    """
    # 1. Try to fetch the full unified connection string first (Production / Cloud)
    unified_url = os.getenv("DATABASE_URL")
    if unified_url:
        # Quick fix: SQLAlchemy requires 'postgresql://', but some cloud hosts provide 'postgres://'
        if unified_url.startswith("postgres://"):
            unified_url = unified_url.replace("postgres://", "postgresql://", 1)
        return unified_url

    # 2. Fall back to your component variables if no unified URL exists (Local Development)
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres") # Ensure this matches your local password!
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "ai_news_aggregator")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


# Initialize the database engine with our dynamic resolution logic
engine = create_engine(get_database_url())

# Production session factory mapping
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """
    Generates a clean SQLAlchemy database session transaction link.
    """
    return SessionLocal()