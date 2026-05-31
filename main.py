"""
================================================================================
🎯 APPLICATION ENTRY POINT: MAIN PIPELINE RUNNER
================================================================================
Description:
  This script serves as the master orchestration switch for the Daily AI News 
  Aggregator. It establishes core logging, ensures the remote PostgreSQL 
  schema and target tables exist via SQLAlchemy, and executes the primary 
  data scraping, LLM curation, and email processing pipeline.
================================================================================
"""

import sys
import logging
from sqlalchemy import text  
from app.daily_runner import run_daily_pipeline
from app.database.connection import engine
from app.database.models import Base

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main(hours: int = 24, top_n: int = 10) -> dict:
    with engine.connect() as conn:
        logger.info("Initializing remote database schema containers...")
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ai_news_aggregator;"))
        conn.commit()
    
    logger.info("Synchronizing cloud database schema models...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database schema synchronized successfully.")
    
    return run_daily_pipeline(hours=hours, top_n=top_n)


if __name__ == "__main__":
    hours = 24
    top_n = 10
    
    # Parse CLI arguments if passed (sys.argv[1] is hours, sys.argv[2] is top_n)
    if len(sys.argv) > 1:
        hours = int(sys.argv[1])
    if len(sys.argv) > 2:
        top_n = int(sys.argv[2])
    
    result = main(hours=hours, top_n=top_n)
    exit(0 if result["success"] else 1)