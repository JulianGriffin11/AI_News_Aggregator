def main(hours: int = 24, top_n: int = 10):
    # 1. Open connection handle to Render's instance
    with engine.connect() as conn:
        logger.info("Initializing remote database schema containers...")
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ai_news_aggregator;"))
        conn.commit()
    
    logger.info("Synchronizing cloud database schema models...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database schema synchronized successfully.")
    
    # 3. Capture the dictionary payload returned by your daily runner engine
    pipeline_result = run_daily_pipeline(hours=hours, top_n=top_n)
    
    # 4. Check if the pipeline purposefully skipped sending an email because it was empty
    if not pipeline_result["success"] and "No digests available" in pipeline_result.get("error", ""):
        logger.info("============================================================")
        logger.info("📢 Quiet Day: No new articles found. Exiting gracefully.")
        logger.info("============================================================")
        # Force a successful status return dictionary so the system exits green!
        return {"success": True, "reason": "No new content to process"}
        
    return pipeline_result


if __name__ == "__main__":
    import sys
    
    hours = 24
    top_n = 10
    
    if len(sys.argv) > 1:
        hours = int(sys.argv[1])
    if len(sys.argv) > 2:
        top_n = int(sys.argv[2])
    
    result = main(hours=hours, top_n=top_n)
    
    # If our graceful check overrode the error, this exits clean with 0!
    exit(0 if result["success"] else 1)