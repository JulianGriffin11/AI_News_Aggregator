"""
================================================================================
🎯 DATA ACCESS LAYER: DECLARATIVE SQLALCHEMY SCHEMA MODELS
================================================================================
Description:
  This module defines the structural database schema layers for the application.
  It uses SQLAlchemy's declarative base models to map out corporate scraping 
  targets (OpenAI and Anthropic) along with synthesized LLM digest tables.
================================================================================
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OpenAIArticle(Base):
    __tablename__ = "openai_articles"
    __table_args__ = {"schema": "ai_news_aggregator"}
    
    guid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AnthropicArticle(Base):
    __tablename__ = "anthropic_articles"
    __table_args__ = {"schema": "ai_news_aggregator"}
    
    guid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Digest(Base):
    __tablename__ = "digests"
    __table_args__ = {"schema": "ai_news_aggregator"}
    
    id = Column(String, primary_key=True)
    article_type = Column(String, nullable=False)
    article_id = Column(String, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

