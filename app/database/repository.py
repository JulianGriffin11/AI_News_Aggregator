"""
================================================================================
🎯 DATA ACCESS LAYER: RELATIONAL REPOSITORY MODULE
================================================================================
Description:
  This module acts as the explicit data access layer for the application. 
  It encapsulates all transactions with the cloud PostgreSQL database using 
  SQLAlchemy Session contexts, managing bulk content caching, duplicate checking, 
  unprocessed article discovery, and rolling digest history generation.
================================================================================
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import OpenAIArticle, AnthropicArticle, Digest  

class Repository:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()
    
    def create_openai_article(self, guid: str, title: str, url: str, published_at: datetime,
                              description: str = "", category: Optional[str] = None, content: Optional[str] = None) -> Optional[OpenAIArticle]:
        existing = self.session.query(OpenAIArticle).filter_by(guid=guid).first()
        if existing:
            return None
        article = OpenAIArticle(
            guid=guid,
            title=title,
            url=url,
            published_at=published_at,
            description=description,
            category=category,
            content=content
        )
        self.session.add(article)
        self.session.commit()
        return article
    
    def create_anthropic_article(self, guid: str, title: str, url: str, published_at: datetime,
                                 description: str = "", category: Optional[str] = None, content: Optional[str] = None) -> Optional[AnthropicArticle]:
        existing = self.session.query(AnthropicArticle).filter_by(guid=guid).first()
        if existing:
            return None
        article = AnthropicArticle(
            guid=guid,
            title=title,
            url=url,
            published_at=published_at,
            description=description,
            category=category,
            content=content
        )
        self.session.add(article)
        self.session.commit()
        return article
    
    def bulk_create_openai_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(OpenAIArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(OpenAIArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category"),
                    content=a.get("content")
                ))
            else:
                if a.get("content"):
                    existing.content = a["content"]
        if new_articles:
            self.session.add_all(new_articles)
        self.session.commit()
        return len(new_articles)
    
    def bulk_create_anthropic_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(AnthropicArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(AnthropicArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category"),
                    content=a.get("content")
                ))
            else:
                if a.get("content"):
                    existing.content = a["content"]
        if new_articles:
            self.session.add_all(new_articles)
        self.session.commit()
        return len(new_articles)
    
    def get_articles_without_digest(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        articles = []
        seen_ids = set()
        
        digests = self.session.query(Digest).all()
        for d in digests:
            seen_ids.add(f"{d.article_type}:{d.article_id}")
        
        openai_articles = self.session.query(OpenAIArticle).all()
        for article in openai_articles:
            key = f"openai:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "openai",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": getattr(article, "content", None) or article.description or "",
                    "published_at": article.published_at
                })
        
        anthropic_articles = self.session.query(AnthropicArticle).all()
        for article in anthropic_articles:
            key = f"anthropic:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "anthropic",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": getattr(article, "content", None) or article.description or "",
                    "published_at": article.published_