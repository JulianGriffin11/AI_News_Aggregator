import logging
from app.daily_runner import run_daily_pipeline
from app.database.connection import engine
from app.database.models import Base
# Import text from SQLAlchemy to allow raw SQL executions
from sqlalchemy import text  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(hours: int = 24, top_n: int = 10):
    # 1. Open a direct connection handle to Render's cloud instance
    with engine.connect() as conn:
        logger.info("Initializing remote database schema containers...")
        # 2. Execute a raw DDL command to safely generate your schema if missing
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ai_news_aggregator;"))
        # 3. Commit the schema generation transaction explicitly
        conn.commit()
    
    logger.info("Synchronizing cloud database schema models...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database schema synchronized successfully.")
    
    return run_daily_pipeline(hours=hours, top_n=top_n)


if __name__ == "__main__":
    import sys
    
    hours = 24
    top_n = 10
    
    if len(sys.argv) > 1:
        hours = int(sys.argv[1])
    if len(sys.argv) > 2:
        top_n = int(sys.argv[2])
    
    result = main(hours=hours, top_n=top_n)
    exit(0 if result["success"] else 1)