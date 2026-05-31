# 🤖 Daily AI News Aggregator Pipeline

An automated, cloud-native data pipeline that monitors premier artificial intelligence research newsrooms, logs updates into a managed relational layer, and delivers a beautifully formatted daily briefing directly to your inbox. 

This architecture leverages a **decoupled compute-and-storage framework**, utilizing free cloud tiers to run continuous daily automation completely on autopilot without infrastructure overhead.

---

## 🏗️ Architecture Overview

The pipeline is split into independent, highly modular operational layers:

1. **Compute Layer (GitHub Actions):** Wakes up automatically every morning at **8:00 AM UTC (4:00 AM EST)** using a scheduled cron job trigger. It provisions a temporary Linux runner, establishes encrypted environment secrets, and fires up the master processing runtime.
2. **Storage Layer (Render PostgreSQL):** A managed relational database instance hosting a secure `ai_news_aggregator` schema that synchronizes table metadata models via SQLAlchemy, preventing any duplicate news logging.
3. **Intelligence & Delivery Layer (Gemini API / SMTP):** Analyzes the raw textual data, checks lookback frames, synthesizes high-quality, professional summaries, and dispatches an elegant corporate briefing via secure email relays.

---

## ⚡ Key Technical Features

* **Zero-Cost Decoupled Deployment:** Sidesteps traditional cloud hosting fees by splitting execution workflows between GitHub's serverless platform and Render's managed database layer.
* **Graceful Exit Safety Net:** Features a custom validation checker that monitors active scraping cycles. If no new research articles are published within the 24-hour lookback window, the system catches the empty pipeline event, logs a `Quiet Day` update, and exits cleanly with green checkmarks rather than crashing.
* **Idempotent Database Syncing:** Utilizes raw schema initialization blocks alongside SQLAlchemy relational models to verify table safety footprints during every single operational cycle.
* **Strict 24-Hour Time Locking:** Programmed with dynamic runtime arguments (`hours=24`) to enforce a tight, rolling curation loop, ensuring no stale data enters your daily digest feeds.

---

## 📂 Repository Structure

```text
├── .github/workflows/
│   └── daily_run.yml        # GitHub Actions Cron scheduling engine configuration
├── app/
│   ├── database/
│   │   ├── connection.py    # Database connection orchestration and connection pool
│   │   └── models.py        # Declarative SQLAlchemy table object definitions
│   ├── services/
│   │   ├── process_digest.py # Interacts with LLM engines to create text summaries
│   │   └── process_email.py  # Assembles core HTML and dispatches secure SMTP email
│   ├── run_scrapers.py      # Targets and extracts target metadata from AI newsrooms
│   └── daily_runner.py      # Core coordination file running stage blocks and safety catches
├── main.py                  # Master entry point script execution wrapper
├── requirements.txt         # Project software dependency Manifest
└── README.md                # Systems architecture documentation