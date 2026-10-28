# Decisions Log

Each entry: what we decided, why, and what we rejected.

## D1: Claude for answers, OpenAI for embeddings (28 Oct 2026)
- **Why:** Claude handles tool calling and structured output well, and matches the target job's stack. Anthropic has no embeddings API; OpenAI's text-embedding-3-small is cheap (~$0.02 per 1M tokens).
- **Rejected:** OpenAI for both (simpler, one key, but less aligned with the job); free-tier APIs (rate limits make eval runs and the live demo unreliable); local models (8GB RAM too weak, can't be hosted for free).

## D2: Fictional company with fake data (28 Oct 2026)
- **Why:** no real client data available; fake data avoids privacy/GDPR issues and lets us design edge cases on purpose (out-of-area leads, missing info, unanswerable questions).
- **Rejected:** scraping a real company's website (legal and privacy risk, no control over gaps).

## D3: Python modules (.py), not notebooks (28 Oct 2026)
- **Why:** a service must be importable, testable (pytest) and runnable by a server.
- **Rejected:** notebooks (good for exploring data, but hard to test, import, or run as a server).

## D4: Secrets in .env + Bitwarden, .gitignore created first (28 Oct 2026)
- **Why:** API keys spend money; leaked keys on GitHub are scraped within minutes. `.env` is ignored by Git; Bitwarden holds the safe master copy.
- **Money safety:** prepaid credit only, auto-reload off, monthly spending limit.

## D5: Generic repo name, branded app name (28 Oct 2026)
- **Why:** repo `ai-lead-assistant` describes reusable code; "Cedar Ridge AI Assistant" gives the demo a realistic face.

## Open decisions
- **API hosting:** Render (simple, free) vs. a VPS with Caddy + systemd (closer to the job, ~$5/month). Decide in session 8.