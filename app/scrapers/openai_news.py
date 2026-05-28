from datetime import datetime, timedelta, timezone
from typing import List, Optional
import feedparser
import requests
from bs4 import BeautifulSoup  # New requirement for lightweight text parsing
from pydantic import BaseModel

# Define the structure of our Article data using Pydantic for validation
class OpenAIArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None
    content: Optional[str] = None  # NEW: Holds the clean full-text body of the article
    

class OpenAIScraper:
    def __init__(self):
        # The target OpenAI RSS feed URL
        self.rss_url = "https://openai.com/news/rss.xml"
        
        # NEW: human web browser profile to prevent OpenAI from blocking our page download
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def get_articles(self, hours: int = 24) -> List[OpenAIArticle]:
        # Parse the RSS feed data from the web
        try:
            resp = requests.get(self.rss_url, headers=self.headers, timeout=10)
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

    def url_to_clean_text(self, url: str) -> Optional[str]:
        """
        NEW METHOD: Downloads the live article webpage, target-strips the layout trash,
        and extracts pure, human-readable text context for your AI Agent.
        Runs lighting-fast with 0% heavy CPU utilization on your Mac!
        """
        try:
            # Download the target web layout
            response = requests.get(url, headers=self.headers, timeout=12)
            if response.status_code != 200:
                return None
                
            # Process the raw HTML content through our parsing layout map
            soup = BeautifulSoup(response.text, "html.parser")
            
            # OpenAI typically wraps its newsroom body text inside an <article> or <main> container
            article_body = soup.find("article") or soup.find("main") or soup.body
            if not article_body:
                return None
                
            # Extract text blocks, separate them with clean line breaks, and strip whitespace padding
            raw_text = article_body.get_text(separator="\n")
            clean_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
            
            return "\n".join(clean_lines)
            
        except Exception as e:
            print(f"Diagnostics: Failed to download/parse full article layout: {e}")
            return None

  
# This ensures the code only runs if executing this file directly
if __name__ == "__main__":
    # Initialize our scraper object
    scraper = OpenAIScraper()
    
    hours_to_check = 50
    print(f"Fetching OpenAI articles from the last {hours_to_check} hours...\n")
    articles: List[OpenAIArticle] = scraper.get_articles(hours=hours_to_check)
    
    # Check if we actually found anything and print the output
    if not articles:
        print("No articles found within that timeframe!")
    else:
        print(f"Found {len(articles)} article(s). Running live text extraction test on Article #1...\n")
        
        target_article = articles[0]
        print(f"Target Title: {target_article.title}")
        print(f"Target URL: {target_article.url}")
        print("-" * 50)
        print("Downloading full page text via lightweight native parser...")
        
        # Test our new lightweight text download utility method
        full_text = scraper.url_to_clean_text(target_article.url)
        
        if full_text:
            print("✓ Text extraction successful! Printing out the first 400 characters:\n")
            print(full_text[:400] + "...\n")
            print("-" * 50)
        else:
            print("⚠️ Failed to parse full-text body.")