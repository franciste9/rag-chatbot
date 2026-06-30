# RAG Chatbot

A simple Retrieval-Augmented Generation (RAG) chatbot built with Python, LangChain, Claude, and Pinecone.

## Features

- 📄 Upload PDF documents
- 🔍 Semantic search across documents
- 💬 Ask questions and get AI-powered answers grounded in your documents
- 📚 Source citation and chunk retrieval

## Tech Stack

- **Backend:** Flask + Python
- **LLM:** Anthropic Claude API
- **Embeddings:** OpenAI text-embedding-3-small
- **Vector DB:** Pinecone
- **Frontend:** HTML + Vanilla JavaScript

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd rag-chatbot
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Get your keys from:
- **Anthropic:** https://console.anthropic.com
- **OpenAI:** https://platform.openai.com
- **Pinecone:** https://www.pinecone.io

### 3. Run the App

```bash
python backend/main.py
```

The API and frontend both run on `http://localhost:5001` — open that URL in a browser to use the app.

## API Endpoints

### Upload Document
```bash
curl -X POST -F "file=@document.pdf" http://localhost:5001/api/documents/upload
```

### Search
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"your search query"}' \
  http://localhost:5001/api/search
```

### Chat
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"your question"}' \
  http://localhost:5001/api/chat
```

## Architecture

```
PDF Upload → Text Extraction → Chunking → Embeddings → Pinecone
                                                           ↓
                                    Query → Embedding → Search → Retrieval
                                                                    ↓
                                                  Context + Query → Claude API → Answer
```

## Key Design Decisions

1. **Chunking Strategy:** Recursive character splitting with overlap for better context preservation
2. **Embeddings:** OpenAI's text-embedding-3-small (fast, cheap, effective)
3. **Vector DB:** Pinecone for simplicity and managed service
4. **LLM:** Claude Sonnet (`claude-sonnet-4-6`) for superior reasoning and RAG performance

## Testing

1. Upload a sample PDF (try a research paper from arXiv)
2. Ask factual questions: "What is the main contribution?"
3. Ask specific details: "What datasets were used?"
4. Observe source citations and relevance

## Performance Notes

- Typical search latency: < 1s
- LLM response time: 2-5s depending on context length
- Embedding generation: ~0.1s per chunk

## Cost Estimation

- OpenAI embeddings: ~$0.02 per 1M tokens
- Claude API: $3-15 per 1M input tokens (depends on model)
- Pinecone: Free tier available (5MB storage)

## Next Steps

- [ ] Multi-user support with conversation history
- [ ] Fine-tuned retrieval reranking
- [ ] Document metadata filtering
- [ ] Streaming responses
- [ ] Deployment (Docker, AWS Lambda, etc.)

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT
