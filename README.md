# Cedar Ridge AI Assistant

An AI assistant for a home-improvement company that answers website visitors from the company's own documents, cites its sources, hands over to a human when it doesn't know, and turns each conversation into a structured lead record.

> Cedar Ridge Roofing & Renovation (Columbus, Ohio) is a fictional company used as demo data. The code is company-agnostic.

## Problem
Home-improvement companies get website visitors at all hours asking the same questions: service areas, price ranges, financing, warranties. Slow answers lose leads to competitors, and the sales team wastes time on visitors who are outside the service area or not ready to buy.

## Aim
- Answer visitor questions **only** from company documents, with **citations**
- **Refuse or hand over to a human** when the documents don't contain the answer
- Produce a **Pydantic-validated JSON lead summary** (service, location, budget, urgency, qualified)
- Log **tokens, cost and latency** for every request
- Measure quality with an **evaluation set** of 40 questions
- Serve it as a **FastAPI** service (used by an n8n automation in project 4) with a **Streamlit** chat demo

## How it works
1. **Knowledge base:** 7 Markdown documents, split into 38 chunks by `##` section (`app/chunking.py`)
2. **Embeddings:** each chunk becomes a 1,536-number vector with OpenAI `text-embedding-3-small` (`app/embeddings.py`)
3. **Storage and search:** chunks + vectors in Supabase (Postgres + pgvector); a SQL function `match_chunks` ranks them by cosine similarity (`sql/schema.sql`, `scripts/ingest.py`, `app/retrieval.py`)
4. **Grounded answers:** the top 5 chunks are passed to Claude Haiku 5.5 as numbered sources; the answer cites them as [1], [2]... Very low similarity (off-topic) hands over without calling Claude (`app/answer.py`)
5. **Lead summary:** a forced tool call fills a Pydantic `LeadSummary` schema; Python rules decide if the lead is qualified and why (`app/schemas.py`, `app/lead.py`)
6. **API:** a FastAPI service exposes it all, with validation, error handling and cost logging (`app/main.py`, `app/costs.py`, `app/logs.py`)

Design decisions and trade-offs are logged in [`decisions.md`](decisions.md).

## API (FastAPI)
Run locally: `uvicorn app.main:app --reload`, then open `http://127.0.0.1:8000/docs`.

| Endpoint | Input | Output |
|---|---|---|
| `GET /health` | – | `{"status": "ok"}` |
| `POST /chat` | `{"question": "..."}` (1-1,000 chars) | answer with [n] citations, sources, handoff |
| `POST /qualify-lead` | `{"conversation": "..."}` (1-5,000 chars) | validated lead JSON, qualified, reasons |

Invalid input returns **422**; failures of OpenAI, Supabase or Claude return a clean **503** (details are logged server-side only). API clients use a 30 s timeout plus the SDKs' automatic retries.

## Evaluation
40 test questions with known answers (`eval/questions.json`): 20 answerable, 5 clear "no", 9 knowledge gaps, 4 multi-part, 2 off-topic. Run with `python -m eval.run_eval`.

| Metric | Result |
|---|---|
| Retrieval hit (right chunk in top 5) | 28 / 29 (97%) |
| Correct facts in the answer | 29 / 29 (100%) |
| Correct handoff (only when it should) | 40 / 40 (100%) |
| Median latency | 2.9 s |

**How the numbers improved:** baseline (threshold 0.35, top 3) refused two valid questions → threshold tuned to 0.20 from measured score distributions → top-5 retrieval fixed one multi-part miss. Every change was re-measured on the full set.

## Cost and latency
Every request logs latency, input/output tokens and cost, to the console and to a Supabase `request_logs` table (Claude Haiku 5.5: $0.10 / $0.50 per million input/output tokens).

| Endpoint | Typical tokens (in / out) | Cost per request |
|---|---|---|
| `/chat` | ~700-800 / ~70-260 | ≈ $0.0002 |
| `/qualify-lead` | ~1,100 / ~190 | ≈ $0.0002 |

That's roughly **5,000 answers per $1**. Very low-similarity (off-topic) questions are handed over without calling Claude, at no LLM cost.

## Code review
Code is written by hand and reviewed with Claude Code in read-only mode (no file edits, no shell commands, no access to `.env`). Review findings fixed so far: crash on empty search results, empty model replies, town normalization ("Columbus, OH"), input limits, API error handling and sync routes.

## Limitations
- One multi-part question still misses a source; broad questions ("tell me about renovation") can miss pricing/timeline chunks.
- Evaluation scoring uses keyword checks (cheap but brittle); an LLM-as-judge would be more robust.
- `sources` lists every retrieved chunk, including ones the answer didn't cite.

## Status
🚧 In progress: session 8 (tests + live deployment)

Done so far: knowledge base, secure key handling (.env + Bitwarden), retrieval with Supabase/pgvector, grounded answers with citations and handoff, Pydantic lead extraction with tool calling, 40-question evaluation, FastAPI service with error handling and per-request cost logging.