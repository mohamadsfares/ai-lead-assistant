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

## D12: Claude Code as a read-only reviewer (10 Nov 2026)
- **Why:** I write the code myself; Claude Code reviews it ("review, don't fix") and I fix the issues. It found failure cases the evaluation couldn't (empty search results, API outages, messy town input like "Columbus, OH").
- **Least privilege:** permission deny rules block reading `.env`, editing files and running shell commands; reviews run in plan mode (read-only), logged in with a subscription, not the project's API key.
- **Fixed now:** empty search → handoff; empty model reply → handoff; town normalization. **Deferred to the FastAPI session:** API error handling, sync vs async routes, input length limits.

## D13: FastAPI service design (12 Nov 2026)
- **Thin endpoints:** routes only validate, call the existing modules and return; all logic stays in `app/`.
- **Sync `def` routes:** the OpenAI, Supabase and Anthropic clients are blocking, so FastAPI runs each request in a thread instead of freezing the event loop.
- **Safety at the door:** Pydantic length limits (422 before any paid call), catch-all error handling that logs details and returns a generic 503, 30 s client timeouts on top of the SDKs' built-in retries.
- **Cost logging:** token usage is returned internally (hidden from callers by `response_model`) and saved per request in `request_logs`; a failed log insert only warns and never breaks the response.
- **Schema descriptions:** urgency values are defined in the Pydantic schema (`Field(description=...)`), which made "active leak" consistently classified as `emergency`.
- **Rejected:** `async def` with sync clients (would block other requests); returning raw error messages to callers (leaks internal details).

## D14: Deploy the API on Render (free tier, Frankfurt) (17 Nov 2026)
- **Why:** simplest path to a live HTTPS URL with no server maintenance; auto-deploys on every push to `main`; free tier is enough for a demo. Region Frankfurt, next to the Supabase database, so every search stays in the same region.
- **Secrets:** production keys (Anthropic, OpenAI, Supabase) are separate from the laptop's dev keys and live only in Render's environment variables and Bitwarden, never in Git or `.env`. Each key can be revoked alone.
- **Python pinned:** `.python-version` = 3.13 (the version we develop and test on).
- **Trade-off:** free instances sleep after 15 min of inactivity; the first request then takes ~1 minute (cold start). Acceptable for a demo; the Streamlit app will show a "waking up" message.
- **Rejected (for now):** a VPS with Caddy + systemd (~$5/month), which is closer to production work but adds server maintenance. Possible later upgrade.
- **Known limitation:** dev and prod share one Supabase database, so request_logs mixes laptop and server rows.

## D15: Streamlit demo as a separate frontend that only calls the API (17-19 Nov 2026)
- **Why:** the UI is only the "face"; all logic, keys and the database stay in the API. The frontend has no secrets, its own `requirements.txt` (streamlit + requests only), and is hosted free on Streamlit Community Cloud from `frontend/`.
- **Design:** two pages with a top menu: a customer chat (history in `session_state`, sources, handoff box, example questions, friendly errors, wake-up ping) and a **Sales team view** that shows the lead extraction (decision, fields, raw JSON). The sales view is labeled as a demo of an internal tool; "Use my chat" connects the two pages.
- **Rejected:** importing the backend code directly into Streamlit (mixes UI and logic, would need the keys in the frontend); `st.tabs` (draws both pages on every run, works badly with the pinned chat box and `st.rerun()`).

## D16: Uptime monitoring with UptimeRobot (19 Nov 2026)
- **Why:** pinging `/health` every 5 minutes keeps the free Render API awake (no cold start for visitors) and sends an email alert if it goes down. `/health` makes no AI calls, so the pings cost nothing.
- **Known limitation:** the Streamlit page can still sleep after a long time without real visitors; open it before sharing the link.
- **Next (planned):** a one-month VPS (session 9b) to host the API and the demo always-on, with Render + Streamlit Cloud kept as a backup.

## D17: Main deployment on a VPS with systemd + Caddy (19 Nov 2026)
- **Why:** no cold starts (free tiers sleep), full control, and it practices the exact stack used in production work: SSH, systemd, Caddy, log management. One server runs both the API and the demo; the demo calls the API over `127.0.0.1` (fast, no internet hop).
- **Security:** SSH key login only, root login and password login disabled, firewall allows only 22/80/443, apps listen only on `127.0.0.1` behind Caddy, `.env` readable only by the app user, the demo service gets no secrets. Hosting account protected with two-step login.
- **Config:** the frontend reads `API_URL` / `PUBLIC_API_URL` from the environment (Render as default), so the same code runs on Streamlit Cloud and on the VPS.
- **Cost:** one month (KVM 1) with auto-renew off; free domain for one year with auto-renew off.
- **Trade-off:** I maintain the server myself (updates, security), and updates are manual (`git pull` + restart) instead of auto-deploy.
- **Backup:** Render + Streamlit Cloud stay online, so the demo survives when the VPS month ends.

## D18: Only cited sources, and an explicit [HANDOFF] signal for gaps (25 Nov 2026)
- **Cited sources:** after Claude answers, a regex reads the `[n]` citations and the API returns only those sources, each keeping its number (`"[4] services.md > ..."`), so the UI matches the answer. Pure function `cited_sources`, covered by 4 tests. The eval's retrieval metric is unaffected (it calls `search()` directly).
- **Gap handoffs:** Claude ends its reply with `[HANDOFF]` only when the sources lack what the customer asked for; the code removes the marker and sets `handoff: true`, so the UI and n8n can react. A clear "no" is a full answer and is not flagged.
- **Evidence:** the first, vague rule over-flagged (handoff 37/40, facts 26/29); a precise rule plus an explicit clear-"no" exception gave handoff 39/40, facts 28/29, median 1.4 s. The remaining miss (q35) is the known multi-part retrieval limit; it is kept visible, not hidden by changing the test.
- **Rejected:** matching phrases in the answer (brittle); a forced tool call returning {answer, handoff} (more robust but more tokens and a bigger change; candidate upgrade if the marker proves unreliable).

## D19: Rate limiting with slowapi (25 Nov 2026)
- **Why:** the API is public and every request spends AI credit; a per-IP limit (20/minute for `/chat`, 10/minute for `/qualify-lead`) stops spam before any paid call and returns 429. `/health` has no limit (uptime pings, no cost).
- **Behind a proxy:** Caddy sends the visitor's IP in `X-Forwarded-For`, and uvicorn trusts it only from `127.0.0.1`, so each visitor gets their own counter on the VPS.
- **Frontend:** a 429 shows "please wait a minute" instead of "not available" (specific `HTTPError` caught before `RequestException`).
- **Known limitation:** demo visitors share one counter (the demo calls the API from the server). Limits were set high enough for normal use; an API key for internal callers is the next step.
- **Rejected:** an in-memory counter written by hand (reinventing a standard library); limiting in Caddy (needs a custom Caddy build with a plugin).

## D20: Frontend tests and a shared config (25 Nov 2026)
- **Frontend tests:** Streamlit's `AppTest` runs the page without a browser; `requests` is faked, so the tests check the page loads, shows answers with sources, and handles a 429, for free and offline.
- **Shared config:** the model name lives in one module (`app/config.py`) used by both `answer.py` and `lead.py`, so a model change can't leave one file behind.