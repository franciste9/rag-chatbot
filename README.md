# RAG Chatbot — Chat over PDFs with Grounded Answers

A Retrieval-Augmented Generation (RAG) chatbot built with Python, LangChain, Claude, and Pinecone. Upload a PDF, ask questions, and get answers grounded in the document's actual content, with source citations for every response.

## Problem Statement

Modern knowledge work requires instant access to information across large document collections. Traditional keyword search is brittle; full-text indexing misses semantic meaning. This project explores **how to build AI systems that answer questions by grounding responses in actual documents** — reducing hallucinations while keeping latency acceptable.

## Features

- 📄 **Upload & Ingest** PDFs with recursive character chunking and overlap
- 🔍 **Semantic Search** using vector similarity (not keyword matching)
- 💬 **Grounded Responses** — Claude answers from retrieved context and is instructed to say "I don't have that information" rather than guess
- 📚 **Source Citations** — every answer shows the chunks (and similarity scores) that informed it
- 🎯 **Document Scoping** — chat is filtered to the uploaded document via Pinecone metadata, so answers don't bleed across uploads

## Architecture

```
INGESTION PIPELINE:
PDF → pypdf Extract → LangChain Chunk (500 chars, 50 overlap) → OpenAI Embed → Pinecone Store

QUERY PIPELINE:
Query → OpenAI Embed → Pinecone Search (cosine, doc_id filter) → Top-5 Chunks → Claude + Context → Grounded Answer
```

## Tech Stack & Rationale

| Component | Technology | Why This Choice |
|-----------|-----------|-----------------|
| **Backend** | Flask + Python | Fast prototyping, rich ML ecosystem |
| **LLM** | Claude (Sonnet) | Strong instruction-following; reliably admits "not in context" instead of fabricating |
| **Embeddings** | OpenAI text-embedding-3-small | Cost-effective, high quality, 1536 dims |
| **Vector DB** | Pinecone | Managed service = no infrastructure overhead; metadata filtering |
| **Orchestration** | LangChain | Standardizes the LLM/embedding interfaces |
| **Frontend** | HTML/CSS/Vanilla JS | Zero dependencies, served by the same Flask process |

### Key Design Decisions

**1. Recursive character chunking (500 chars, 50 overlap)**
Splits on paragraph/sentence boundaries first, falling back to smaller separators, so chunks tend to end at natural breaks. The 50-character overlap preserves references that straddle chunk boundaries. (Character-based, not token-based — simpler, and adequate at this scale.)

**2. Document scoping via metadata filter**
All chunks live in one Pinecone index keyed `{doc_id}_{chunk_index}`. Queries pass a `doc_id` metadata filter so retrieval is scoped to the document the user uploaded — without it, answers could cite unrelated uploads.

**3. Claude for generation, OpenAI for embeddings**
Deliberately polyglot: embeddings are a commodity priced per token (3-small is among the cheapest quality options), while generation quality and refusal behavior matter most for grounding — Claude is strong at answering only from provided context.

**4. Pinecone over self-hosted pgvector**
No infrastructure to manage for a portfolio-scale project; free tier is sufficient; metadata filtering and batched upserts (100/batch) come built in.

## Evaluation

Honest status: **no automated evals yet.** Retrieval and answer quality are currently verified manually via the scripts in `tests/`, which exercise the real APIs end-to-end (upload → retrieve → answer) and print scores and answers for inspection.

Planned next (in CI): a golden question set per sample PDF with retrieval precision@k and answer-groundedness checks as a merge gate. Until those numbers exist, this README doesn't claim any.

## Quick Start

### 1. Environment Setup

```bash
git clone <your-repo>
cd rag-chatbot
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get API Keys

- **Anthropic:** https://console.anthropic.com/
- **OpenAI:** https://platform.openai.com/
- **Pinecone:** https://app.pinecone.io (free tier available)

### 3. Configure

```bash
cp .env.example .env
# Edit .env with your API keys
# Pinecone: create an index named "rag-index" (dimension: 1536, metric: cosine)
```

### 4. Run

```bash
python backend/main.py
# Open: http://localhost:5001
```

## API Endpoints

### Upload Document
```bash
curl -X POST -F "file=@paper.pdf" http://localhost:5001/api/documents/upload
```

**Response:**
```json
{
  "filename": "paper.pdf",
  "doc_id": "3f2a…",
  "num_chunks": 42,
  "text_length": 15234,
  "status": "processed"
}
```

### Search Documents
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"What is the main contribution?","top_k":5,"doc_id":"3f2a…"}' \
  http://localhost:5001/api/search
```

### Chat with a Document
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"Summarize the methodology","doc_id":"3f2a…"}' \
  http://localhost:5001/api/chat
```

**Response:**
```json
{
  "query": "Summarize the methodology",
  "answer": "The methodology uses...",
  "sources": [
    {"text": "...", "score": 0.89, "doc_id": "3f2a…", "chunk_index": 4}
  ]
}
```

`doc_id` is optional on both endpoints; omitting it searches across all uploaded documents.

## Testing

`tests/` contains end-to-end scripts (not a pytest suite yet) that run against the real Anthropic/OpenAI/Pinecone APIs — running them costs real API credits:

```bash
python tests/test_pinecone.py   # env → Pinecone init → PDF processing → store → search → quality check
python tests/test_chat.py       # process a PDF → retrieve → call Claude → print answers
```

`tests/create_sample_pdf.py` and `tests/create_nba_pdf.py` generate the sample PDFs the scripts use. Converting these to a pytest suite with mocked clients is on the roadmap.

## Current Limitations

- **Single-turn:** no conversation history — each question stands alone
- **No document management:** no deletion endpoint; the index accumulates uploads (distinguished by `doc_id`)
- **No caching:** every query re-embeds; identical queries pay twice
- **No automated evals or monitoring:** quality is verified manually (see Evaluation)
- **No auth:** anyone with the URL can upload and query

## Path to Production

**Phase 1 (this project):** working RAG pipeline — ingestion → scoped retrieval → grounded chat, deployed with gunicorn behind a 10 MB upload cap.

**Phase 2:** eval harness in CI (golden set, precision@k, groundedness), conversation history, document deletion + per-user namespaces, caching, structured observability.

**Phase 3:** reranking, streaming responses, multi-document synthesis, feedback loop.

## Deployment

Deployed via the included `Procfile` (gunicorn, 2 workers, binds to `$PORT`):

```bash
# Railway: connect the repo, set the four env vars, deploy.
# DEBUG must remain unset/False in production.
```

The same Flask process serves both the API and the frontend, so a single service is all that's needed.

## Repository Structure

```
rag-chatbot/
├── backend/
│   ├── main.py              # Flask app: routes, upload cap, error handling
│   ├── ingestion.py         # PDF → chunks → embeddings
│   ├── retrieval.py         # Pinecone store/search with doc_id filtering
│   ├── chat.py              # Claude prompt construction + generation
│   ├── config.py            # Env vars + startup validation
│   └── utils.py             # Helpers
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── tests/                   # End-to-end scripts (real APIs, see Testing)
├── samplepdf/               # Generated sample PDFs
├── Procfile
├── .env.example
├── requirements.txt
└── README.md
```

## License

MIT

---

**Built with:** Python, Flask, LangChain, Claude, OpenAI, Pinecone
**Status:** Working proof-of-concept, deployed; eval harness in progress
