"""
================================================================================
🎯 SERVICE LAYER: LLM USER PROFILE CURATION LAYER
================================================================================
Description:
  This module serves as the personalization engine. It extracts recent AI news
  summaries from the storage layer and passes them directly to the Curator Agent
  to score, rank, and document contextual reasoning metrics matching your target
  demographic or interest background matrix.
================================================================================
"""

import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from app.agent.curator_agent import CuratorAgent
from app.profiles.user_profile import USER_PROFILE
from app.database.repository import Repository

load_dotenv()

# Resolve path mappings for standalone execution scripts
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def curate_digests(hours: int = 24) -> dict:
    curator = CuratorAgent(USER_PROFILE)
    repo = Repository()
    
    digests = repo.get_recent_digests(hours=hours)
    total = len(digests)
    
    if total == 0:
        logger.warning(f"No recent database digests discovered inside the last {hours} hour window.")
        return {"total": 0, "ranked": 0}
    
    logger.info(f"Evaluating {total} digests against target metric vector profile: '{USER_PROFILE.get('name', 'Default')}'...")
    ranked_articles = curator.rank_digests(digests)
    
    if not ranked_articles:
        logger.error("Core profile algorithm failed to calculate relevancy metrics across data slice.")
        return {"total": total, "ranked": 0}
    
    logger.info(f"✓ Profile matrix matching resolved. Successfully ranked {len(ranked_articles)} items.")
    
    return {
        "total": total,
        "ranked": len(ranked_articles),
        "articles": [
            {
                "digest_id": a.digest_id,
                "rank": a.rank,
                "relevance_score": a.relevance_score,
                "reasoning": a.reasoning
            }
            for a in ranked_articles
        ]
    }


if __name__ == "__main__":
    curation_metrics = curate_digests(hours=24)
    logger.info(f"Local Dry Run Summary -> {curation_metrics}")