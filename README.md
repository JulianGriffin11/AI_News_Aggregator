
# AI News Aggregator — Project Plan and Guide

This repository contains the source code and materials for a live build of an AI-powered news aggregator. The goal is to scrape AI-focused content (YouTube, public feeds), generate short digests using an LLM, rank content for a sample user profile, and optionally send a daily email digest.

This README is written for beginners and contains a clear plan you can follow to run, extend, and learn from the project.

## Quick overview

- Purpose: collect recent AI-related content, summarize it with an LLM, rank results for a user, and provide a daily digest via email.
- Main entry point: `main.py` — runs the daily pipeline (scrape → process → digest → email).
- Key folders:
	- `app/scrapers/` — scrapers (YouTube, other sources)
	- `app/agent/` — small LLM-based agents (digest, curator, email)
	- `app/database/` — DB connection, models, and repository helpers
	- `app/services/` — processing helpers (digest creation, email sending)
	- `app/profiles/` — example user profile used for ranking/personalization

## Project phases (branches)

- `master` — local setup and core functionality (scraping, DB, agents, local email)
- `deployment` — add Docker, compose, and deployment configuration
- `deployment-final` — production hardening and optimizations

If you're following along with the live video, use these branches as checkpoints.

## High-level architecture

1. Scrapers collect new content and store raw items in the database.
2. Processing services clean and enrich content (e.g., fetch transcripts, extract text).
3. Agents run the plan → ask → edit loop using an LLM to summarize, rank, and generate email text.
4. Repository layer saves digests and metadata.
5. Email service delivers the final digest.

### Agent loop (plan → ask → edit) — beginner explanation

- Plan: build prompts and rules for what the LLM should do (e.g., "Summarize this video transcript in 3 sentences").
- Ask: call the LLM (OpenAI or Anthropic) with the prompt and receive text output.
- Edit: post-process the model output (trim length, fix formatting, validate) and save it.

This loop is used by the digest agent (summaries), curator agent (ranking), and email agent (subject + body).

## Getting started (minimum steps)

1. Create a virtual environment and install dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `requirements.txt` is missing, check `pyproject.toml` for dependencies and install them with pip.

2. Copy example env and set secrets:

```bash
cp app/example.env .env
# Edit .env and set OPENAI_API_KEY, POSTGRES_URL (or DB settings), MY_EMAIL, APP_PASSWORD
```

3. Start Postgres (optional) — Docker Compose is included for convenience:

```bash
docker-compose -f docker/docker-compose.yml up -d
```

4. Create DB tables:

```bash
python app/database/create_tables.py
```

5. Run the pipeline (basic):

```bash
python main.py
```

This runs the daily pipeline which scrapes recent content, enriches it, runs the agents, writes digests to the DB, and can send an email if configured.

## Commands you will use while developing

- Run scrapers only:

```bash
python -c "from app.runner import run_scrapers; print(run_scrapers(hours=24))"
```

- Generate digests (process content in DB):

```bash
python app/services/process_digest.py
```

- Send the email digest (dry-run vs live depends on env):

```bash
python app/services/process_email.py
```

## Development plan — step-by-step (follow this to learn)

Phase A — Local core (master)

1. Verify the DB connection and create tables.
2. Run scrapers for one channel and inspect raw items in the DB.
3. Make the transcript fetching robust (retries, proxy support is already present in `app/scrapers/youtube.py`).
4. Implement or inspect the digest agent — confirm it can produce a short summary for one item.
5. Implement the curator agent to score items for a sample profile.
6. Wire the digest + curator results into a small HTML email template.
7. Test sending an email to yourself (use an app password for security).

Phase B — Deployment (deployment branch)

1. Add Dockerfiles and docker-compose to run the app + Postgres.
2. Add a small healthcheck and a periodic runner (cron or scheduler) to trigger `main.py`.
3. Secure secrets with environment variables and, if desired, use a secrets manager for production.

Phase C — Production-ready (deployment-final)

1. Add monitoring (logging, alerting) and optimize LLM usage (batch prompts, smaller models).
2. Harden retry logic for scrapers and transient network errors.
3. Add tests and CI workflows.

## Testing & quality checks

- Start with a couple of unit tests for utility functions (parsing video IDs, formatting timestamps).
- Add a test that runs a small end-to-end pipeline using a local SQLite DB or a test Postgres container.
- If you change agent prompts, add snapshot tests to assert the output shape and some expected tokens.

## Common troubleshooting tips

- Missing transcripts: some videos don't have captions — the scraper gracefully skips these.
- Rate limits: LLM APIs have rate limits. If you see errors, reduce parallelism and add retries/backoff.
- DB connection errors: confirm `POSTGRES_URL` or individual DB vars match your local Postgres.

## Where to look next in the codebase

- Pipeline orchestration: `app/daily_runner.py`
- Scrapers and ingestion: `app/runner.py` and `app/scrapers/` (e.g. `youtube.py`)
- Agents (plan/ask/edit): `app/agent/` — contains `digest_agent.py`, `curator_agent.py`, `email_agent.py`.
- Database models and repository: `app/database/models.py` and `app/database/repository.py`.
- Services: `app/services/process_*` which coordinate agent usage and output formatting.

## Roadmap & learning goals

- Week 1: Understand the end-to-end pipeline and run the local version.
- Week 2: Improve prompts, add another source (e.g., RSS or Twitter/X), and add tests.
- Week 3: Containerize and deploy; add monitoring and scheduling.

## Final notes (security & privacy)

Treat API keys, email passwords, and DB credentials as secrets. Do not commit them. Use `.env` locally and a proper secret store in production.

If you want, I can:
- Add a minimal `requirements.txt` from `pyproject.toml` if it's missing.
- Add a small example test that validates `youtube.py` helpers (video ID parsing).
- Walk through one agent file and add inline comments so the flow is crystal clear.

Tell me which of the above you'd like next and I'll implement it.

