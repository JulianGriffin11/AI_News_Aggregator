"""
================================================================================
🎯 SERVICE LAYER: DYNAMIC CURATION & EMAIL DISPATCH
================================================================================
Description:
  This module pulls recent AI news summaries from the database, runs them through
  the Curator and Email Agents to score and rank them against your personalized
  user profile. It then synthesizes a clean email digest.
================================================================================
"""

import logging
from datetime import datetime
from dotenv import load_dotenv
from app.agent.email_agent import EmailAgent, RankedArticleDetail, EmailDigestResponse
from app.agent.curator_agent import CuratorAgent
from app.profiles.user_profile import USER_PROFILE
from app.database.repository import Repository
from app.services.email import send_email, digest_to_html

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def generate_email_digest(hours: int = 24, top_n: int = 10) -> EmailDigestResponse:
    curator = CuratorAgent(USER_PROFILE)
    email_agent = EmailAgent(USER_PROFILE)
    repo = Repository()
    
    digests = repo.get_recent_digests(hours=hours)
    total = len(digests)
    
    if total == 0:
        logger.warning(f"No database digests found within the last {hours} hours window.")
        raise ValueError("No digests available")
    
    logger.info(f"Ranking {total} digests for email generation...")
    ranked_articles = curator.rank_digests(digests)
    
    if not ranked_articles:
        logger.error("Failed to execute LLM profile ranking on raw articles.")
        raise ValueError("Failed to rank articles")
    
    logger.info(f"Generating email digest structures with top {top_n} articles...")
    
    article_details = [
        RankedArticleDetail(
            digest_id=a.digest_id,
            rank=a.rank,
            relevance_score=a.relevance_score,
            reasoning=a.reasoning,
            title=next((d["title"] for d in digests if d["id"] == a.digest_id), ""),
            summary=next((d["summary"] for d in digests if d["id"] == a.digest_id), ""),
            url=next((d["url"] for d in digests if d["id"] == a.digest_id), ""),
            article_type=next((d["article_type"] for d in digests if d["id"] == a.digest_id), "")
        )
        for a in ranked_articles
    ]
    
    email_digest = email_agent.create_email_digest_response(
        ranked_articles=article_details,
        total_ranked=len(ranked_articles),
        limit=top_n
    )
    
    logger.info("Email digest payload synthesized successfully.")
    return email_digest


def send_digest_email(hours: int = 24, top_n: int = 10) -> dict:
    try:
        result = generate_email_digest(hours=hours, top_n=top_n)
        markdown_content = result.to_markdown()
        html_content = digest_to_html(result)
        
        # Parse greeting details dynamically to build out a clean subject line string
        date_string = result.introduction.greeting.split("for ")[-1] if "for " in result.introduction.greeting else "Today"
        subject = f"Daily AI News Digest - {date_string}"
        
        send_email(
            subject=subject,
            body_text=markdown_content,
            body_html=html_content
        )
        
        logger.info("Email packet delivered to SMTP gateway successfully.")
        return {
            "success": True,
            "subject": subject,
            "articles_count": len(result.articles)
        }
    except ValueError as e:
        logger.error(f"Execution bypassed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    run_result = send_digest_email(hours=24, top_n=10)
    logger.info(f"Local Execution Result Summary -> {run_result}")
