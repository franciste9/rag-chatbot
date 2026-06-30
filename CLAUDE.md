# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A RAG (Retrieval-Augmented Generation) chatbot: upload PDFs, ask questions, get Claude-generated answers grounded in retrieved chunks, with source citations. Flask backend, vanilla HTML/JS frontend.

Stack: Flask, LangChain (`langchain-anthropic`, `langchain-openai`), Claude (chat), OpenAI `text-embedding-3-small` (embeddings), Pinecone (vector store), pypdf (PDF text extraction).

## Setup & running

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY, OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME

python backend/main.py   # runs Flask on http://localhost:5001 (also serves the frontend at /)
```

There is no build step and no linter/formatter configured.

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
- `backend/retrieval.py::RetrieverService` — owns the Pinecone client/index; `store_chunks` upserts `(id, embedding, metadata)` tuples keyed `{doc_id}_{chunk_index}` in batches of 100 (Pinecone limit); `search` embeds the query, queries Pinecone with `include_metadata=True`, and accesses results via **attribute access** (`results.matches`, `match.score`, `match.metadata`) — not dict-style — as required by Pinecone SDK v3+.
- `backend/chat.py::ChatService` — wraps `ChatAnthropic`; `build_prompt` concatenates retrieved chunks into a single context block before calling `.invoke()`.

`backend/main.py` wires these together behind three routes (`/api/documents/upload`, `/api/search`, `/api/chat`), plus a catch-all static-file route that serves `frontend/` (so the frontend is served from the same Flask process as the API, not a separate dev server). A global Flask `errorhandler` catches all exceptions and returns `{error, type}` as JSON with a 500.

`backend/config.py` centralizes env var reads and exposes `validate_config()`, `DEBUG`, and `PORT`. `backend/main.py` imports `config` directly and calls `config.validate_config()` at module load time (so the app fails fast on startup if any required API key is missing), and passes `config.DEBUG`/`config.PORT` to `app.run()`. The individual service classes (`RetrieverService`, etc.) still read their own env vars directly via `os.getenv` inside `__init__`.

`init_services()` lazily constructs all three service singletons behind a `threading.Lock` (`_init_lock`) to prevent duplicate construction under concurrent cold-start requests. Uploaded filenames are sanitized with `werkzeug.utils.secure_filename` before use in temp paths.

There's no document-deletion endpoint and no per-document namespacing in Pinecone — all chunks from all uploaded documents live in one flat index, distinguished only by the `doc_id` chunk metadata.
