# 📦 Core Application Modules

This folder contains all the core code that makes the news aggregator run. It handles fetching data, talking to the AI model, saving to the database, and sending the final email.

---

## 📂 Folder Breakdown

*   **`scrapers/`** — Code that collects fresh content from the web, like YouTube channels, AI newsrooms, and RSS feeds.
*   **`agent/`** — The AI logic that uses an LLM to summarize, rank, and format the news using the **Plan ➔ Ask ➔ Edit** loop.
*   **`database/`** — The database setups and helper files used to read and write data to your cloud PostgreSQL database.
*   **`services/`** — Background tools that clean up raw text data and securely handle sending out the daily email digests.
*   **`profiles/`** — User profiles containing specific interests used by the AI to rank and personalize the news for you.