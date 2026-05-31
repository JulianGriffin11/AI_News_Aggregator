"""
================================================================================
🎯 EXTRACTION LAYER: CORPORATE OPENAI RSS & TEXT SCRAPER
================================================================================
Description:
  This scraper module targets the official OpenAI corporate newsroom RSS feed.
  It isolates published articles matching a rolling time-window constraint, 
  downloads the destination article page layouts, and parses raw text blocks 
  using a lightweight BeautifulSoup engine to feed structured data to the LLM.
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


class OpenAIArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None
    content: Optional[str] = None  


class OpenAIScraper:
    def __init__(self):
        self.rss_url = "https://openai.com/news/rss.xml"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def get_articles(self, hours: int = 24) -> List[OpenAIArticle]:
        try:
            resp = requests.get(self.rss_url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
        except Exception:
            feed = feedparser.parse(self.rss_url)
            
        if not feed.entries:
            return []
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        articles = []
        
        for entry in feed.entries:
            published_parsed = getattr(entry, "published_parsed", None)
            if not published_parsed:
                continue
            
            published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
            
            if published_time >= cutoff_time:
                articles.append(OpenAIArticle(
                    title=entry.get("title", ""),
                    description=entry.get("description", ""),
                    url=entry.get("link", ""),
                    guid=entry.get("id", entry.get("link", "")),
                    published_at=published_time,
                    category=entry.get("tags", [{}])[0].get("term") if entry.get("tags") else None
                ))
        
        return articles

    def url_to_clean_text(self, url: str) -> Optional[str]:
        try:
            response = requests.get(url, headers=self.headers, timeout=12)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, "html.parser")
            article_body = soup.find("article") or soup.find("main") or soup.body
            if not article_body:
                return None
                
            raw_text = article_body.get_text(separator="\n")
            clean_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
            
            return "\n".join(clean_lines)
            
        except Exception as e:
            logger.error(f"Failed to extract text footprint from layout destination: {e}")
            return None

  
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = OpenAIScraper()
    
    hours_to_check = 50
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