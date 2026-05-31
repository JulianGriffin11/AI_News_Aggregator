import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Importing your exact file names from your workspace
from app.run_scrapers import run_scrapers
from app.services.process_digest import process_digests  # Plural! Matches your file definition
from app.services.process_email import send_digest_email  # Your email runner function

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def run_daily_pipeline(hours: int = 24, top_n: int = 10) -> dict:
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("Starting Daily AI News Aggregator Pipeline")
    logger.info("=" * 60)
    
    results = {
        "start_time": start_time.isoformat(),
        "scraping": {},
        "digests": {},
        "email": {},
        "success": False
    }
    
    try:
        # --------------------------------------------------------
        # STAGE 1: RUN THE SCRAPERS
        # --------------------------------------------------------
        logger.info("\n[1/3] Scraping articles from sources...")
        scraping_results = run_scrapers(hours=hours)
        results["scraping"] = {
            "openai": len(scraping_results.get("openai", [])),
            "anthropic": len(scraping_results.get("anthropic", []))
        }
        logger.info(f"✓ Scraped {results['scraping']['openai']} OpenAI articles, "
                    f"{results['scraping']['anthropic']} Anthropic articles")

        # --------------------------------------------------------
        # STAGE 2: CREATE SUMMARIES (UNIFIED DIGEST ENGINE)
        # --------------------------------------------------------
        logger.info("\n[2/3] Creating digests for articles...")
        digest_result = process_digests()
        results["digests"] = digest_result
        logger.info(f"✓ Created {digest_result['processed']} digests "
                    f"({digest_result['failed']} failed out of {digest_result['total']} total)")
        
        # --------------------------------------------------------
        # CRITICAL SAFETY CHECK: INTERCEPT ZERO-ARTICLE QUIET DAYS
        # --------------------------------------------------------
        if digest_result.get("processed", 0) == 0:
            logger.info("\n============================================================")
            logger.info("📢 Quiet Day: No new articles to process. Bypassing email.")
            logger.info("============================================================")
            
            # Formulate a successful response early, bypassing Stage 3's crash condition completely
            results["success"] = True
            results["email"] = {
                "success": True,
                "status": "Skipped",
                "reason": "No digests available for the current execution window"
            }
            
            # Log the successful exit metrics block immediately
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            results["end_time"] = end_time.isoformat()
            results["duration_seconds"] = duration
            
            logger.info("\n" + "=" * 60)
            logger.info("Pipeline Summary")
            logger.info("=" * 60)
            logger.info(f"Duration: {duration:.1f} seconds")
            logger.info(f"Scraped: {results['scraping']}")
            logger.info(f"Digests: {results['digests']}")
            logger.info("Email: Skipped (No Content)")
            logger.info("=" * 60)
            return results

        # --------------------------------------------------------
        # STAGE 3: PERSONALIZED CURATION AND EMAIL TRANSMISSION
        # --------------------------------------------------------
        logger.info("\n[3/3] Generating and sending email digest...")
        email_result = send_digest_email(hours=hours, top_n=top_n)
        results["email"] = email_result
        
        if email_result["success"]:
            logger.info(f"✓ Email sent successfully with {email_result['articles_count']} articles")
            results["success"] = True
        else:
            logger.error(f"✗ Failed to send email: {email_result.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        results["error"] = str(e)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    results["end_time"] = end_time.isoformat()
    results["duration_seconds"] = duration
    
    # --------------------------------------------------------
    # FINAL EXECUTION SUMMARY LOG (FOR NORMAL EMAIL RUNS)
    # --------------------------------------------------------
    logger.info("\n" + "=" * 60)
    logger.info("Pipeline Summary")
    logger.info("=" * 60)
    logger.info(f"Duration: {duration:.1f} seconds")
    logger.info(f"Scraped: {results['scraping']}")
    logger.info(f"Digests: {results['digests']}")
    logger.info(f"Email: {'Sent' if results['success'] else 'Failed'}")
    logger.info("=" * 60)
    
    return results


if __name__ == "__main__":
    result = run_daily_pipeline(hours=24, top_n=10)
    exit(0 if result["success"] else 1)