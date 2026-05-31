# 🤖 AI News Aggregator

Welcome to the **Daily AI News Aggregator Pipeline**! This repository contains the source code for a **production-ready, AI-powered data pipeline**. The system automatically extracts AI-focused research updates and public engineering logs, synthesizes concise digests using a Large Language Model (LLM), and delivers a personalized daily email briefing directly to your inbox.

---

## ⚡ Quick Overview

*   **Core Purpose:** Efficiently collect recent AI-related content, summarize it via an LLM, rank the results based on user preferences, and provide a clean daily digest via email.
*   **Main Entry Point:** `main.py` — Coordinates and executes the daily pipeline workflow on a loop: **Scrape ➔ Process ➔ Digest ➔ Email**.

---

## 🌿 Project Branches

*   **`main`** — Local workspace setup and core backend functionality (scraping, database models, LLM agents, local email testing).
*   **`deployment`** — Cloud infrastructure addition and basic deployment automation configuration.
*   **`final_deployment`** — Production hardening, advanced error trapping, and quiet-day optimizations.

---

## 🏗️ High-Level Architecture

1.  **Scrapers:** Collect fresh content from target newsrooms and store raw metadata items securely in the database.
2.  **Processing Services:** Clean, parse, and enrich text content (e.g., stripping markdown, verifying time-windows).
3.  **AI Agents:** Execute a custom **Plan ➔ Ask ➔ Edit** orchestration loop using an LLM to summarize, rank, and generate engaging email text.
4.  **Repository Layer:** Interacts with the relational database to save generated digests, track history, and prevent duplicate logs.
5.  **Email Service:** Builds the final responsive HTML container and delivers the briefing via secure **SMTP relays**.

### 🔄 Agent Loop (Plan ➔ Ask ➔ Edit) — Beginner Explanation

*   **Plan:** Build dynamic prompts and strict operational rules for the LLM (e.g., *"Summarize this technical article in exactly 3 bullet points"*).
*   **Ask:** Fire the payload over to the LLM (**Gemini API**) with your instructions and receive the raw textual generation.
*   **Edit:** Post-process the model's output (trim white space, sanitize string inputs, validate structure) before saving.

> 💡 **System Note:** This exact engineering loop is utilized by the **Digest Agent** (summaries), **Curator Agent** (ranking), and **Email Agent** (subject lines + body copy).

---

## ⚙️ Cloud Infrastructure Layers

The pipeline is completely split into independent, highly modular operational layers:

*   🖥️ **Compute (GitHub Actions):** Wakes up automatically every morning at **4:00 AM EST** using a scheduled **cron job trigger**. It provisions a temporary Linux container environment, injects encrypted repository secrets, and fires up the master execution script.
*   🗄️ **Storage (Render PostgreSQL):** A managed relational database cloud instance hosting a secure `ai_news_aggregator` schema. It synchronizes data models via **SQLAlchemy ORM** to ensure robust data persistence.
*   🧠 **Intelligence (Gemini API):** Processes the raw scraped text, manages lookback evaluation frames, and synthesizes high-quality summaries on autopilot.

---

## 🚀 Getting Started & Local Run

Feel free to run this entire pipeline locally on your machine!
