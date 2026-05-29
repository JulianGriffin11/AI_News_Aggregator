import os
from typing import Optional
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv

# Ingest your .env hidden file parameters
load_dotenv()


# This Pydantic model defines the structured blueprint Gemini must return
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
        # The modern unified client entry point
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"
        self.system_prompt = PROMPT

    def generate_digest(self, title: str, content: str, article_type: str) -> Optional[DigestOutput]:
        """
        Connects to Gemini via modern client architecture and forces a structured JSON 
        response mapping directly back to our DigestOutput object without any retry logic.
        """
        try:
            user_prompt = f"Create a digest for this {article_type}: \n Title: {title} \n Content: {content[:8000]}"

            # Build the configuration using the modern types module layout
            config = types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                temperature=0.7,
                response_mime_type="application/json",
                response_schema=DigestOutput,
            )

            # Fire off the structural generation request instantly
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config
            )
            
            if response and response.text:
                return DigestOutput.model_validate_json(response.text)
                
            return None
            
        except Exception as e:
            print(f"Diagnostics: Structured content digest generation failed: {e}")
            return None