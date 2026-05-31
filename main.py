import logging
from app.daily_runner import run_daily_pipeline
from app.database.connection import engine
from app.database.models import Base
# ────────────────────────────────────────────────
from sqlalchemy import text  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(hours: int = 24, top_n: int = 10):
    with engine.connect() as conn:
        logger.info("Initializing remote database schema containers...")
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ai_news_aggregator;"))
        conn.commit()
    
    logger.info("Synchronizing cloud database schema models...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database schema synchronized successfully.")
    
    # Wrap the pipeline run in a try/except block to trap inner crashes!
    try:
        pipeline_result = run_daily_pipeline(hours=hours, top_n=top_n)
        return pipeline_result
    except Exception as e:
        # Check if the text of the crash is our expected "No digests available" message
        error_msg = str(e)
        if "No digests available" in error_msg:
            logger.info("============================================================")
            logger.info("📢 Quiet Day: No new articles found. Exiting gracefully.")
            logger.info("============================================================")
            # Return a clean success dictionary so the app exits with code 0!
            return {"success": True, "reason": "No new content to process"}
        
        # If it's a completely different error (like an invalid API key), re-raise it so it rightly fails
        logger.error(f"Pipeline encountered an unexpected critical error: {error_msg}")
        raise e


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