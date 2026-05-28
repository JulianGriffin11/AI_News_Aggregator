from typing import List
from app.scrapers.openai_news import OpenAIScraper, OpenAIArticle
from .scrapers.anthropic_news import AnthropicScraper, AnthropicArticle
from .database.repository import Repository


def run_scrapers(hours: int = 24) -> dict:
    """
    Streamlined core aggregator that harvests high-density text articles 
    directly from tier-1 AI corporate newsrooms.
    """
    openai_scraper = OpenAIScraper()
    anthropic_scraper = AnthropicScraper()
    repo = Repository()
    
    # 1. Harvest OpenAI Corporate News
    print(f"Scanning OpenAI newsroom for articles in the last {hours} hours...")
    openai_articles = openai_scraper.get_articles(hours=hours)
    
    # 2. Harvest Anthropic Corporate News
    print(f"Scanning Anthropic newsroom for articles in the last {hours} hours...")
    anthropic_articles = anthropic_scraper.get_articles(hours=hours)
    
    # 3. Commit OpenAI data to the database
    if openai_articles:
        article_dicts = [
            {
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category
            }
            for a in openai_articles
        ]
        repo.bulk_create_openai_articles(article_dicts)
        print(f"Successfully cached {len(openai_articles)} OpenAI articles.")
    else:
        print("No new OpenAI articles found within time window.")
    
    # 4. Commit Anthropic data to the database
    if anthropic_articles:
        article_dicts = [
            {
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category
            }
            for a in anthropic_articles
        ]
        repo.bulk_create_anthropic_articles(article_dicts)
        print(f"Successfully cached {len(anthropic_articles)} Anthropic articles.")
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
    
    results = run_scrapers(hours=48)
    
    print("\n" + "=" * 60)
    print("AGGREGATION RUN SUMMARY:")
    print(f"  ✓ OpenAI Articles Gathered:   {len(results['openai'])}")
    print(f"  ✓ Anthropic Articles Gathered: {len(results['anthropic'])}")
    print("=" * 60)