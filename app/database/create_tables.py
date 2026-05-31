"""
================================================================================
🎯 STORAGE LAYER: MANUAL SCHEMA INITIALIZATION UTILITY
================================================================================
Description:
  This administrative utility script manually triggers SQLAlchemy's metadata
  engine to generate table definitions on the remote PostgreSQL server. 
  
  Note: This operation is handled automatically by the master 'main.py' entry
  point during production runs, making this file strictly optional. Keep for manual tests.
================================================================================
"""

import sys
import logging
from pathlib import Path
from app.database.models import Base
from app.database.connection import engine

# Ensure relative package routes parse correctly during direct terminal execution
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Triggering manual database metadata synchronization layout...")
    Base.metadata.create_all(engine)
    logger.info("✓ Cloud relational structures initialized successfully.")
