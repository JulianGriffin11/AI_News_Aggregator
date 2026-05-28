from typing import List
from app.scrapers.openai_news import OpenAIScraper, OpenAIArticle
from .scrapers.anthropic_news import AnthropicScraper, AnthropicArticle
from .database.repository import Repository


def run_scrapers(hours: int = 24) -> dict:
    """
    Streamlined core aggregator that harvests high-density text articles 
    directly from tier-1 AI corporate newsrooms and downloads full body text.
    """
    openai_scraper = OpenAIScraper()
    anthropic_scraper = AnthropicScraper()
    repo = Repository()
    
    # 1. Harvest OpenAI Corporate News Items
    print(f"Scanning OpenAI newsroom for articles in the last {hours} hours...")
    openai_articles = openai_scraper.get_articles(hours=hours)
    
    # 2. Harvest Anthropic Corporate News Items
    print(f"Scanning Anthropic newsroom for articles in the last {hours} hours...")
    anthropic_articles = anthropic_scraper.get_articles(hours=hours)
    
    # 3. Process and Commit OpenAI Data
    if openai_articles:
        print(f"\nProcessing {len(openai_articles)} OpenAI articles...")
        openai_dicts = []
        for a in openai_articles:
            print(f" -> Downloading full webpage layout text for: '{a.title[:40]}...'")
            # Trigger our new lightweight HTML text stripper!
            full_text_body = openai_scraper.url_to_clean_text(a.url)
            
            openai_dicts.append({
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category,
                "content": full_text_body  # NEW: Passes text string straight to repository!
            })
            
        repo.bulk_create_openai_articles(openai_dicts)
        print(f"✓ Successfully cached {len(openai_articles)} OpenAI articles into Postgres.")
    else:
        print("No new OpenAI articles found within time window.")
    
    # 4. Process and Commit Anthropic Data
    if anthropic_articles:
        print(f"\nProcessing {len(anthropic_articles)} Anthropic articles...")
        anthropic_dicts = []
        for a in anthropic_articles:
            print(f" -> Downloading full webpage layout text for: '{a.title[:40]}...'")
            
            # NOTE: Make sure your anthropic_scraper class file has the exact same 
            # url_to_clean_text parsing method implemented as your openai_scraper!
            full_text_body = anthropic_scraper.url_to_clean_text(a.url)
            
            anthropic_dicts.append({
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category,
                "content": full_text_body  # NEW: Passes text string straight to repository!
            })
            
        repo.bulk_create_anthropic_articles(anthropic_dicts)
        print(f"✓ Successfully cached {len(anthropic_articles)} Anthropic articles into Postgres.")
    else:
        print("No new Anthropic articles found within time window.")
    
    return {
        "openai": openai_articles,
        "anthropic": anthropic_articles,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("LAUNCHING STREAMLINED AI NEWS AGGREGATOR PRODUCTION PIPELINE")
    print("=" * 60)
    
    # Check the last 48 hours for data uploads
    results = run_scrapers(hours=48)
    
    print("\n" + "=" * 60)
    print("AGGREGATION RUN SUMMARY:")
    print(f"  ✓ OpenAI Articles Processed:   {len(results['openai'])}")
    print(f"  ✓ Anthropic Articles Processed: {len(results['anthropic'])}")
    print("=" * 60)