"""
================================================================================
🎯 SERVICE LAYER: UNIFIED LLM DIGEST ENGINE
================================================================================
Description:
  This module pulls raw scraped content from the PostgreSQL database that lacks
  an active digest entry. It coordinates passing the payloads directly to the
  structured Pydantic generation layer using the Gemini API and commits the
  resulting technical summaries back to the cloud storage layer.
================================================================================
"""

import sys
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from app.agent.digest_agent import DigestAgent
from app.database.repository import Repository

load_dotenv()

# Ensure internal package structures are resolved correctly during individual file execution
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def process_digests(limit: Optional[int] = None) -> dict:
    agent = DigestAgent()
    repo = Repository()
    
    articles = repo.get_articles_without_digest(limit=limit)
    total = len(articles)
    processed = 0
    failed = 0
    
    logger.info(f"Starting digest processing loop for {total} new items...")
    
    for idx, article in enumerate(articles, 1):
        article_type = article["type"]
        article_id = article["id"]
        
        # Keep terminal log tracking outputs looking concise
        clean_title = article["title"][:50] + "..." if len(article["title"]) > 50 else article["title"]
        logger.info(f"[{idx}/{total}] Processing {article_type}: '{clean_title}' (ID: {article_id})")
        
        try:
            digest_result = agent.generate_digest(
                title=article["title"],
                content=article["content"],
                article_type=article_type
            )
            
            if digest_result:
                repo.create_digest(
                    article_type=article_type,
                    article_id=article_id,
                    url=article["url"],
                    title=digest_result.title,
                    summary=digest_result.summary,
                    published_at=article.get("published_at")
                )
                processed += 1
                logger.info(f"✓ Successfully cached digest model footprint for ID: {article_id}")
            else:
                failed += 1
                logger.warning(f"✗ Core engine generation dropped empty response for ID: {article_id}")
        except Exception as e:
            failed += 1
            logger.error(f"✗ Processing failure encountered on ID {article_id}: {e}")
            
    logger.info(f"Batch completed execution: {processed} resolved | {failed} dropped | {total} total.")
    
    return {
        "total": total,
        "processed": processed,
        "failed": failed
    }


if __name__ == "__main__":
    run_metrics = process_digests()
    logger.info(f"Local Dry Run Summary -> {run_metrics}")