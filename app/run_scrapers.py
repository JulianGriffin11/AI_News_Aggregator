"""
================================================================================
🎯 AGGREGATION LAYER: CORPORATE NEWSROOM SCRAPER CORE
================================================================================
Description:
  This module orchestrates the extraction of fresh research logs and technical
  announcements directly from tier-1 AI newsrooms (OpenAI and Anthropic).
================================================================================
"""

import logging
from app.scrapers.openai_news import OpenAIScraper
from .scrapers.anthropic_news import AnthropicScraper
from .database.repository import Repository

logger = logging.getLogger(__name__)


def run_scrapers(hours: int = 24) -> dict:
    openai_scraper = OpenAIScraper()
    anthropic_scraper = AnthropicScraper()
    repo = Repository()
    
    logger.info(f"Scanning OpenAI newsroom for articles in the last {hours} hours...")
    openai_articles = openai_scraper.get_articles(hours=hours)
    
    logger.info(f"Scanning Anthropic newsroom for articles in the last {hours} hours...")
    anthropic_articles = anthropic_scraper.get_articles(hours=hours)
    
    # Process OpenAI Data
    if openai_articles:
        logger.info(f"Processing {len(openai_articles)} OpenAI articles...")
        openai_dicts = []
        for a in openai_articles:
            logger.info(f" -> Extracting full text: '{a.title[:40]}...'")
            full_text_body = openai_scraper.url_to_clean_text(a.url)
            
            openai_dicts.append({
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category,
                "content": full_text_body  
            })
            
        repo.bulk_create_openai_articles(openai_dicts)
        logger.info(f"✓ Cached {len(openai_articles)} OpenAI articles into Postgres.")
    else:
        logger.info("No new OpenAI articles found within time window.")
    
    # Process Anthropic Data
    if anthropic_articles:
        logger.info(f"Processing {len(anthropic_articles)} Anthropic articles...")
        anthropic_dicts = []
        for a in anthropic_articles:
            logger.info(f" -> Extracting full text: '{a.title[:40]}...'")
            full_text_body = anthropic_scraper.url_to_clean_text(a.url)
            
            anthropic_dicts.append({
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category,
                "content": full_text_body  
            })
            
        repo.bulk_create_anthropic_articles(anthropic_dicts)
        logger.info(f"✓ Cached {len(anthropic_articles)} Anthropic articles into Postgres.")
    else:
        logger.info("No new Anthropic articles found within time window.")
    
    return {
        "openai": openai_articles,
        "anthropic": anthropic_articles,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("LAUNCHING STREAMLINED AI NEWS AGGREGATOR PRODUCTION PIPELINE")
    
    results = run_scrapers(hours=24)
    
    logger.info(f"Run Summary -> OpenAI: {len(results['openai'])} | Anthropic: {len(results['anthropic'])}")