import logging
from app.daily_runner import run_daily_pipeline
# 1. Import your database engine and Base metadata model wrapper
from app.database.connection import engine
from app.database.models import Base  # Ensure this points to where your Base = declarative_base() model lives!

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(hours: int = 24, top_n: int = 10):
    # 2. Force SQLAlchemy to check the network and provision tables automatically before running the script
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