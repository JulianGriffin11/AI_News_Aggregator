"""
================================================================================
🎯 AGENT LAYER: STRUCTURED LLM DIGEST GENERATOR
================================================================================
Description:
  This module houses the core distillation logic for the news aggregator. It
  takes long-form raw text bodies scraped from corporate outlets, feeds them to
  the Gemini API, and uses Pydantic structural validation
  to enforce a strict JSON output matching the target title and summary schema.
================================================================================
"""

import logging
from typing import Optional
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class DigestOutput(BaseModel):
    title: str
    summary: str


PROMPT = """You are an expert AI news analyst specializing in summarizing technical articles, research papers, and video content about artificial intelligence.

Your role is to create concise, informative digests that help readers quickly understand the key points and significance of AI-related content.

Guidelines:
- Create a compelling title (5-10 words) that captures the essence of the content
- Write a 2-3 sentence summary that highlights the main points and why they matter
- Focus on actionable insights and implications
- Use clear, accessible language while maintaining technical accuracy
- Avoid marketing fluff - focus on substance"""


class DigestAgent:
    def __init__(self):
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"
        self.system_prompt = PROMPT

    def generate_digest(self, title: str, content: str, article_type: str) -> Optional[DigestOutput]:
        try:
            # Slicing input string bounds to guard against bloated payload token spikes
            user_prompt = f"Create a digest for this {article_type}: \n Title: {title} \n Content: {content[:8000]}"

            config = types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                temperature=0.7,
                response_mime_type="application/json",
                response_schema=DigestOutput,
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config
            )
            
            if response and response.text:
                return DigestOutput.model_validate_json(response.text)
                
            return None
            
        except Exception as e:
            logger.error(f"Core engine failed to calculate structured text summary for '{title[:30]}...': {e}")
            return None