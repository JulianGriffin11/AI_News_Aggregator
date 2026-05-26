from datetime import datetime, timedelta, timezone
from typing import List, Optional
import feedparser
import requests
from pydantic import BaseModel

# Define the structure of our Article data using Pydantic for validation
class OpenAIArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None
    

class OpenAIScraper:
    def __init__(self):
        # The target OpenAI RSS feed URL
        self.rss_url = "https://openai.com/news/rss.xml"
        # REMOVED DOCLING HERE — It was never being used anyway!

    def get_articles(self, hours: int = 24) -> List[OpenAIArticle]:
        # Parse the RSS feed data from the web
        # Use requests (which bundles certifi) to avoid local macOS SSL issues,
        # falling back to feedparser fetching directly if requests fails.
        try:
            resp = requests.get(self.rss_url, timeout=10)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
        except Exception:
            feed = feedparser.parse(self.rss_url)
        if not feed.entries:
            return []
        
        # Establish our time window constraint
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=hours)
        articles = []
        
        # Loop through every article found in the feed
        for entry in feed.entries:
            published_parsed = getattr(entry, "published_parsed", None)
            if not published_parsed:
                continue
            
            # Convert the time structural tuple into a timezone-aware datetime object
            published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
            
            # Filter: Only keep articles published within our cutoff window
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

  
# This ensures the code only runs if executing this file directly
if __name__ == "__main__":
    # Initialize our scraper object
    scraper = OpenAIScraper()
    
    # Let's set hours to 500 so we actually catch historical data on the feed
    hours_to_check = 50
    print(f"Fetching OpenAI articles from the last {hours_to_check} hours...\n")
    articles: List[OpenAIArticle] = scraper.get_articles(hours=hours_to_check)
    
    # Check if we actually found anything and print the output
    if not articles:
        print("No articles found within that timeframe!")
    else:
        print(f"Found {len(articles)} article(s):\n")
        for index, article in enumerate(articles, start=1):
            print(f"--- Article #{index} ---")
            print(f"Title: {article.title}")
            print(f"Published: {article.published_at}")
            print(f"URL: {article.url}")
            print(f"Category: {article.category}")
            print(f"Description: {article.description}\n")