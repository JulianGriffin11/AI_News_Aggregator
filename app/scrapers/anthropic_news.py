from datetime import datetime, timedelta, timezone
from typing import List, Optional
import feedparser
import requests
from bs4 import BeautifulSoup  # Lightweight, Intel-Mac safe alternative to docling!
from pydantic import BaseModel

# Define the structure of our Anthropic Article data
class AnthropicArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None


class AnthropicScraper:
    def __init__(self):
        # The list of target Anthropic RSS feeds hosted on GitHub
        self.rss_urls = [
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
        ]

    def get_articles(self, hours: int = 24) -> List[AnthropicArticle]:
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=hours)
        articles = []
        seen_guids = set()
        
        for rss_url in self.rss_urls:
            # Use requests to cleanly bypass macOS Monterey SSL issues
            try:
                resp = requests.get(rss_url, timeout=10)
                resp.raise_for_status()
                feed = feedparser.parse(resp.content)
            except Exception as e:
                print(f"Network log: Skipping feed {rss_url} due to connection error: {e}")
                continue
                
            if not feed.entries:
                continue
            
            for entry in feed.entries:
                published_parsed = getattr(entry, "published_parsed", None)
                if not published_parsed:
                    continue
                
                published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                
                # Time filter validation window
                if published_time >= cutoff_time:
                    guid = entry.get("id", entry.get("link", ""))
                    # Prevent duplicates across the 3 different feeds
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
        # Clean alternative to docling using BeautifulSoup to fetch raw text content safely
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")
            
            # Extract plain text content from the article webpage body
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            return f"Could not extract webpage content: {e}"


if __name__ == "__main__":
    scraper = AnthropicScraper()
    
    # Let's use 200 hours so we are guaranteed to catch historical data for this test run!
    hours_to_check = 200
    print(f"Fetching Anthropic articles from the last {hours_to_check} hours...\n")
    articles: List[AnthropicArticle] = scraper.get_articles(hours=hours_to_check)
    
    if not articles:
        print("No articles found within that timeframe!")
    else:
        print(f"Successfully found {len(articles)} article(s)!\n")
        
        # Print the details of the first article
        first_article = articles[0]
        print(f"--- Top Article Details ---")
        print(f"Title: {first_article.title}")
        print(f"Published: {first_article.published_at}")
        print(f"URL: {first_article.url}\n")
        
        # Safely scrape and clean the text of that specific article webpage
        print("Scraping webpage text content content safely...")
        webpage_text = scraper.url_to_clean_text(first_article.url)
        print("\n--- Snippet of Extracted Webpage Text ---")
        # Print just the first 500 characters so your terminal isn't overwhelmed
        print(webpage_text[:500] + "\n... [Truncated] ...")