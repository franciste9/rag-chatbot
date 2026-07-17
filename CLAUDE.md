# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A RAG (Retrieval-Augmented Generation) chatbot: upload PDFs, ask questions, get Claude-generated answers grounded in retrieved chunks, with source citations. Flask backend, vanilla HTML/JS frontend.

Stack: Flask, LangChain (`langchain-anthropic`, `langchain-openai`), Claude (chat), OpenAI `text-embedding-3-small` (embeddings), Pinecone (vector store), pypdf (PDF text extraction). Dependencies are pinned exactly in `requirements.txt` — keep them pinned; don't reintroduce open ranges.

Sprint context: this is the Week 1 project of an 8-week AI engineering portfolio sprint. A CI eval harness (golden question set, retrieval precision@k, groundedness checks) is the planned Week 2 addition — the README's Evaluation section intentionally claims no metrics until that harness produces real numbers. Keep README claims strictly in sync with implemented behavior.

## Setup & running

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY, OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME

python backend/main.py   # runs Flask on http://localhost:5001 (also serves the frontend at /)
```

`DEBUG` defaults to **False** (`backend/config.py`); set `DEBUG=True` in `.env` for local auto-reload. Never enable it in production — Werkzeug's debugger allows arbitrary code execution.

There is no build step and no linter/formatter configured.

## Deployment

Production runs via the `Procfile`: `gunicorn --chdir backend --workers 2 --timeout 120 --bind 0.0.0.0:$PORT main:app` (the 120s timeout accommodates embedding large PDF uploads). Target platform is Railway: connect the repo, set the four env vars, deploy. The frontend uses a relative `/api` base URL and is served by the same Flask process, so a single service suffices. Uploads are capped at 10 MB via `MAX_CONTENT_LENGTH` with a JSON 413 handler.

## Tests

There is no pytest suite — `tests/` contains standalone scripts run directly with `python`, each exercising the real Anthropic/OpenAI/Pinecone APIs (no mocking):

```bash
python tests/test_pinecone.py   # end-to-end: env vars -> Pinecone init -> PDF processing -> store -> search -> quality check
python tests/test_chat.py       # end-to-end: process a PDF -> retrieve -> call Claude -> print answers
```

Both scripts hardcode a PDF path (`/Users/francis.te/Github/rag-chatbot/sample5pages.pdf`) that must exist locally; `tests/create_sample_pdf.py` and `tests/create_nba_pdf.py` generate sample PDFs for this purpose. Running these scripts calls real, billed external APIs.

## Architecture

Pipeline:

```
PDF Upload -> extract_text_from_pdf -> chunk_text -> generate_embeddings -> Pinecone upsert
                                                                                  |
                                          Query -> embed_query -> Pinecone search -> chunks
                                                                                  |
                                                          chunks + query -> Claude -> answer
```

Three backend services, each a thin wrapper around one external dependency, instantiated lazily as module-level globals in `backend/main.py::init_services()` (not per-request, not dependency-injected):

- `backend/ingestion.py::DocumentProcessor` — pypdf text extraction, LangChain `RecursiveCharacterTextSplitter` (chunk_size=500, overlap=50), OpenAI embeddings.
- `backend/retrieval.py::RetrieverService` — owns the Pinecone client/index; `store_chunks` upserts `(id, embedding, metadata)` tuples keyed `{doc_id}_{chunk_index}` in batches of 100 (Pinecone limit); `search` embeds the query, queries Pinecone with `include_metadata=True` and an optional `doc_id` metadata filter (`{'doc_id': {'$eq': ...}}`), and accesses results via **attribute access** (`results.matches`, `match.score`, `match.metadata`) — not dict-style — as required by Pinecone SDK v3+.
- `backend/chat.py::ChatService` — wraps `ChatAnthropic`; `build_prompt` concatenates retrieved chunks into a single context block before calling `.invoke()`.

`backend/main.py` wires these together behind three routes (`/api/documents/upload`, `/api/search`, `/api/chat`), plus a catch-all static-file route that serves `frontend/` (so the frontend is served from the same Flask process as the API, not a separate dev server). A global Flask `errorhandler` catches all exceptions and returns `{error, type}` as JSON with a 500.

`backend/config.py` centralizes env var reads and exposes `validate_config()`, `DEBUG`, and `PORT`. `backend/main.py` imports `config` directly and calls `config.validate_config()` at module load time (so the app fails fast on startup if any required API key is missing), and passes `config.DEBUG`/`config.PORT` to `app.run()`. The individual service classes (`RetrieverService`, etc.) still read their own env vars directly via `os.getenv` inside `__init__`.

`init_services()` lazily constructs all three service singletons behind a `threading.Lock` (`_init_lock`) to prevent duplicate construction under concurrent cold-start requests. Uploaded filenames are sanitized with `werkzeug.utils.secure_filename` before use in temp paths.

Per-IP rate limiting via Flask-Limiter: upload `5 per hour`, chat `20 per hour`, search `30 per hour` (limit strings live in `backend/config.py` as `RATE_LIMIT_UPLOAD`/`RATE_LIMIT_CHAT`/`RATE_LIMIT_SEARCH`, overridable via same-named env vars), default `200 per hour` for anything else; `/api/health` and the static/frontend routes are `@limiter.exempt`. The WSGI app is wrapped in `ProxyFix` (`x_for=1`) so `request.remote_addr` is the real client IP behind Railway's single proxy hop. A 429 handler returns `{"error": ...}` JSON with `Retry-After` (via `headers_enabled=True`). Caveat: `storage_uri="memory://"` means counters are per gunicorn worker — with 2 workers, effective limits can be up to 2× (Redis is the production fix).

`/api/search` and `/api/chat` accept an optional `doc_id`; when present, retrieval is scoped to that document via the Pinecone metadata filter. The frontend (`frontend/script.js`) stores the `doc_id` returned by the most recent upload in `currentDocId` and sends it with every chat request, so the UI always chats against the last-uploaded document. Omitting `doc_id` searches across all documents.

There's no document-deletion endpoint and no per-document namespacing in Pinecone — all chunks from all uploaded documents live in one flat index, distinguished by `doc_id` chunk metadata (used for query-time filtering, not isolation).

## Roadmap (near-term)

Planned, in order: convert `tests/` to pytest with mocked API clients (removing the hardcoded absolute PDF path), then the Week 2 eval harness in CI. Conversation history, document deletion, and caching are known gaps documented in the README's Current Limitations.
