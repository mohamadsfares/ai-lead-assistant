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

## D6: Claude Haiku 5.5 for answers (29 Oct 2026)
- **Why:** fastest and lowest-cost Claude model; the task is answering from provided documents, which doesn't need the most powerful model. The first test call cost a fraction of a cent.
- **Rejected:** Sonnet/Opus (higher cost and latency, not needed yet). We revisit if the evaluation shows quality problems.

## D7: Chunk by `##` headings, with a "Doc title > Section" prefix (3 Nov 2026)
- **Why:** the documents were written with one topic per `##` section, so each chunk is complete and focused, and citations can name the exact section. The prefix keeps similar headings apart (e.g. "Price Ranges > Roofing" vs "Warranty > Roofing Warranty").
- **Rejected:** fixed-size chunks (e.g. every 500 characters), which cut sentences and topics in half.
- **Known limitation:** the FAQ section becomes one large chunk mixing several questions. Split by `###` only if the evaluation shows weak results. (Evaluation result: FAQ questions all passed, so no split needed.)

## D8: Supabase (Postgres + pgvector) in Central EU (Frankfurt) (3 Nov 2026)
- **Why:** one managed database for document vectors now and leads later (project 4); SQL search with pgvector; free tier. EU region for GDPR data residency and low latency from Lebanon. RLS enabled; the backend uses the secret key only.
- **Rejected:** a local vector store (e.g. Chroma), simpler but with no SQL, no shared database for project 4, and harder to deploy.

## D9: Similarity threshold for human handoff (5 Nov 2026)
- **Why:** if the best chunk scores below the threshold, the answer is very likely not in the documents, so the bot hands over to a human without calling Claude (no guessing, no cost). First observed scores: answerable ≈ 0.59, related ≈ 0.43, gap ≈ 0.25. Started at 0.35.
- **Status:** superseded by D11 after evaluation.
- **Known limitation:** multi-part questions ("gutter guards + solar panels?") can miss one part's chunk, because one question = one vector.

## D10: Lead extraction with forced tool calling + Pydantic; qualification rules in Python (9 Nov 2026)
- **Why:** a forced tool call