
# AI News Aggregator — Project Plan and Guide

This repository contains the source code for a production-ready, AI-powered news aggregator pipeline. The system automatically extracts AI-focused research updates and public engineering logs, synthesizes concise digests using a Large Language Model (LLM), and delivers a personalized daily email briefing directly to your inbox.

## Quick overview

- Purpose: collect recent AI-related content, summarize it with an LLM, rank results for a user, and provide a daily digest via email.
- Main entry point: `main.py` — runs the daily pipeline (scrape → process → digest → email).

## Project phases (branches)

- `main` — local setup and core functionality (scraping, DB, agents, local email)
- `deployment` — add basic deployment configuration
- `final_deployment` — production hardening and optimizations

## High-level architecture

1. Scrapers collect new content and store raw items in the database.
2. Processing services clean and enrich content (e.g., fetch transcripts, extract text).
3. Agents run the plan → ask → edit loop using an LLM to summarize, rank, and generate email text.
4. Repository layer saves digests and metadata.
5. Email service delivers the final digest.

### Agent loop (plan → ask → edit) — beginner explanation

- Plan: build prompts and rules for what the LLM should do (e.g., "Summarize this video transcript in 3 sentences").
- Ask: call the LLM (Gemini 2.5 Flash) with the prompt and receive text output.
- Edit: post-process the model output (trim length, fix formatting, validate) and save it.

This loop is used by the digest agent (summaries), curator agent (ranking), and email agent (subject + body).

## 🏗️ Architecture Overview

The pipeline is split into independent, highly modular operational layers:

1. **Compute (GitHub Actions):** Wakes up automatically every morning at **4:00 AM EST** using a scheduled cron job trigger. It provisions a temporary Linux runner, establishes encrypted environment secrets, and fires up the master processing runtime.
2. **Storage (Render PostgreSQL):** A managed relational database instance hosting a secure `ai_news_aggregator` schema that synchronizes table metadata models via SQLAlchemy, preventing any duplicate news logging.
3. **Intelligence (Gemini API):** Analyzes the raw textual data, checks lookback frames, synthesizes high-quality, professional summaries, and dispatches an elegant corporate briefing via secure email relays.

---
