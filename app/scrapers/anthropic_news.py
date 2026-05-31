"""
================================================================================
🎯 EXTRACTION LAYER: CORPORATE ANTHROPIC MULTI-FEED & TEXT SCRAPER
================================================================================
Description:
  This scraper module targets Anthropic's newsroom, research, and engineering
  logs via dedicated multi-feed RSS mirrors. It enforces lookback window filters,
  deduplicates cross-cutting announcements, and parses raw text content blocks
  using a lightweight BeautifulSoup parser layer.
================================================================================
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import feedparser
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AnthropicArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None


class AnthropicScraper:
    def __init__(self):
        self.rss_urls = [
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
        ]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def get_articles(self, hours: int = 24) -> List[AnthropicArticle]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        articles = []
        seen_guids = set()
        
        for rss_url in self.rss_urls:
            try:
                resp = requests.get(rss_url, headers=self.headers, timeout=10)
                resp.raise_for_status()
                feed = feedparser.parse(resp.content)
            except Exception as e:
                logger.error(f"Network log: Skipping feed {rss_url} due to connection error: {e}")
                continue
                
            if not feed.entries:
                continue
            
            for entry in feed.entries:
                published_parsed = getattr(entry, "published_parsed", None)
                if not published_parsed:
                    continue
                
                published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                
                if published_time >= cutoff_time:
                    guid = entry.get("id", entry.get("link", ""))
                    if guid not in seen_guids:
                        seen_guids.add(guid)
                        articles.append(AnthropicArticle(
                            title=entry.get("title", ""),
                            description=entry.get("description", ""),
                            url=entry.get("link", ""),
                            guid=guid,
                            published_at=published_time,
                            category=entry.get("tags", [{}])[0].get("term") if entry.get("tags") else None
                        ))
        
        return articles

    def url_to_clean_text(self, url: str) -> Optional[str]:
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            logger.error(f"Failed to extract text footprint from layout destination: {e}")
            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = AnthropicScraper()
    
    hours_to_check = 200
    logger.info(f"Executing dry run scanning frame for the last {hours_to_check} hours...")
    extracted_articles = scraper.get_articles(hours=hours_to_check)
    
    if not extracted_articles:
        logger.info("No corporate log targets located inside this window frame.")
    else:
        target = extracted_articles[0]
        logger.info(f"Target located -> Title: {target.title} | Link: {target.url}")
        
        full_text = scraper.url_to_clean_text(target.url)
        if full_text:
            logger.info(f"✓ Extraction verified. Sample payload preview:\n{full_text[:200]}...")
        else:
            logger.warning("⚠️ Payload processing returned an empty structure string.")