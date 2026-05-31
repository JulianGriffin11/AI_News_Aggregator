"""
================================================================================
🎯 AGENT LAYER: STRUCTURED LLM EMAIL SYNTHESIZER
================================================================================
Description:
  This module defines the structured Pydantic models and executive runtime logic
  for the Email Agent. It leverages the native Google GenAI API and a dedicated
  system instruction prompt to generate personalized, conversational email 
  introductions and output validated JSON objects matching your target schema.
================================================================================
"""

import logging
from datetime import datetime
from typing import List, Optional
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class EmailIntroduction(BaseModel):
    greeting: str = Field(description="Personalized greeting with user's name and date")
    introduction: str = Field(description="2-3 sentence overview of what's in the top 10 ranked articles")


class RankedArticleDetail(BaseModel):
    digest_id: str
    rank: int
    relevance_score: float
    title: str
    summary: str
    url: str
    article_type: str
    reasoning: Optional[str] = None


class EmailDigestResponse(BaseModel):
    introduction: EmailIntroduction
    articles: List[RankedArticleDetail]
    total_ranked: int
    top_n: int
    
    def to_markdown(self) -> str:
        markdown_str = f"{self.introduction.greeting}\n\n"
        markdown_str += f"{self.introduction.introduction}\n\n"
        markdown_str += "---\n\n"
        
        for article in self.articles:
            markdown_str += f"## {article.title}\n\n"
            markdown_str += f"{article.summary}\n\n"
            markdown_str += f"[Read more →]({article.url})\n\n"
            markdown_str += "---\n\n"
        
        return markdown_str


EMAIL_PROMPT = """You are an expert email writer specializing in creating engaging, personalized AI news digests.

Your role is to write a warm, professional introduction for a daily AI news digest email that:
- Greets the user by name
- Includes the current date
- Provides a brief, engaging overview of what's coming in the top 10 ranked articles
- Highlights the most interesting or important themes
- Sets expectations for the content ahead

Keep it concise (2-3 sentences for the introduction), friendly, and professional."""


class EmailAgent:
    def __init__(self, user_profile: dict):
        self.client = genai.Client()
        self.model = "gemini-2.5-flash"
        self.user_profile = user_profile

    def generate_introduction(self, ranked_articles: List) -> EmailIntroduction:
        current_date = datetime.now().strftime('%B %d, %Y')
        
        if not ranked_articles:
            return EmailIntroduction(
                greeting=f"Hey {self.user_profile['name']}, here is your daily digest of AI news for {current_date}.",
                introduction="No articles were ranked today."
            )
        
        top_articles = ranked_articles[:10]
        article_summaries = "\n".join([
            f"{idx + 1}. {article.title if hasattr(article, 'title') else article.get('title', 'N/A')} (Score: {article.relevance_score if hasattr(article, 'relevance_score') else article.get('relevance_score', 0):.1f}/10)"
            for idx, article in enumerate(top_articles)
        ])
        
        user_prompt = f"""Create an email introduction for {self.user_profile['name']} for {current_date}.

Top 10 ranked articles:
{article_summaries}

Generate a greeting and introduction that previews these articles."""

        try:
            config = types.GenerateContentConfig(
                system_instruction=EMAIL_PROMPT,
                temperature=0.7,  
                response_mime_type="application/json",
                response_schema=EmailIntroduction,
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config
            )
            
            if response and response.text:
                intro = EmailIntroduction.model_validate_json(response.text)
                
                if not intro.greeting.startswith(f"Hey {self.user_profile['name']}"):
                    intro.greeting = f"Hey {self.user_profile['name']}, here is your daily digest of AI news for {current_date}."
                
                return intro
                
            raise ValueError("Empty response text returned from Gemini SDK.")
            
        except Exception as e:
            logger.error(f"Email Agent failed to generate structured introduction via LLM: {e}")
            return EmailIntroduction(
                greeting=f"Hey {self.user_profile['name']}, here is your daily digest of AI news for {current_date}.",
                introduction="Here are the top 10 AI news articles ranked by relevance to your interests."
            )
    
    def create_email_digest_response(self, ranked_articles: List[RankedArticleDetail], total_ranked: int, limit: int = 10) -> EmailDigestResponse:
        top_articles = ranked_articles[:limit]
        introduction = self.generate_introduction(top_articles)
        
        return EmailDigestResponse(
            introduction=introduction,
            articles=top_articles,
            total_ranked=total_ranked,
            top_n=limit
        )