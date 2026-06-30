# RAG Chatbot Test Suite

## Overview
This directory contains unit and integration tests for the RAG chatbot system.

## Test Files

### 1. `test_pinecone.py` - Pinecone Integration Test
Tests vector storage, retrieval, and semantic search functionality.

**What it tests:**
- Environment variables configuration
- Pinecone connection and authentication
- PDF document processing
- Chunk creation and embeddings
- Vector storage in Pinecone
- Semantic search functionality
- Retrieval quality metrics

**Run:**
```bash
source venv/bin/activate
python tests/test_pinecone.py
```

**Expected output:**
- ✅ All 7 tests pass
- Retrieval scores > 0.75 (target quality)
- Response time metrics

---

### 2. `test_chat.py` - Chat Endpoint Test
Tests the full RAG pipeline: retrieval → Claude API → grounded answers.

**What it tests:**
- Service initialization (DocumentProcessor, RetrieverService, ChatService)
- PDF processing and storage
- Retrieval of relevant chunks
- Claude API integration
- Answer grounding in context
- Latency measurement

**Run:**
```bash
source venv/bin/activate
python tests/test_chat.py
```

**Expected output:**
- ✅ Chat responses grounded in PDF
- Response time < 5 seconds
- No hallucinations (Claude respects context)

---

### 3. `create_sample_pdf.py` - Generate Sample PDF
Creates a 1-page sample PDF with Machine Learning content for testing.

**What it creates:**
- `sample1page.pdf` (1 page, ~2KB)
- Well-structured ML fundamentals content
- Good for semantic search and retrieval testing

**Run:**
```bash
source venv/bin/activate
python tests/create_sample_pdf.py
```

---

## Test Workflow

### Step 1: Generate Sample PDF
```bash
python tests/create_sample_pdf.py
# Creates: sample1page.pdf
```

### Step 2: Test Pinecone Integration
```bash
python tests/test_pinecone.py
# Validates: Vector storage, search, retrieval quality
```

### Step 3: Test Chat Endpoint
```bash
python tests/test_chat.py
# Validates: Full RAG pipeline, Claude integration
```

### Step 4: Manual Browser Test
```bash
python backend/main.py
# Open: http://localhost:5001
# Upload sample1page.pdf
# Test queries and chat
```

---

## Success Criteria

| Test | Metric | Target | Status |
|------|--------|--------|--------|
| Pinecone | Retrieval Score | > 0.75 | ⚠️ Currently 0.3-0.4 |
| Chat | Response Time | < 5s | ✅ |
| Chat | Grounded Answers | No hallucinations | ✅ |
| Chat | Claude Integration | 200 response | ✅ |

---

## Known Issues

### Low Retrieval Scores (0.3-0.4)
The semantic similarity scores are lower than the target 0.75. This is likely due to the chunking strategy (500 chars with 50 char overlap).

**Solution (Week 2):**
- Test chunk sizes: 800-1000 chars
- Increase overlap: 100-150 chars
- Use domain-specific PDFs for better relevance

### Model Not Found Error
If you see: `Error code: 404 - model: claude-3-5-sonnet-20241022`

**Solution:** Update `backend/chat.py` to use latest model:
```python
self.llm = ChatAnthropic(model="claude-sonnet-4-6")
```

---

## Debugging

### Enable Verbose Logging
```bash
export LOG_LEVEL=DEBUG
python tests/test_pinecone.py
```

### Check API Keys
```bash
cat .env | grep -E "ANTHROPIC|OPENAI|PINECONE"
```

### Test Individual Services
```python
# Test Pinecone only
from backend.retrieval import RetrieverService
retriever = RetrieverService()
results = retriever.search("test query")
```

---

## Next Steps

1. **Week 2 Optimization:**
   - Optimize chunking strategy
   - Improve retrieval scores to > 0.75
   - Add caching for performance
   - Add structured logging

2. **Production Hardening:**
   - Add comprehensive error handling
   - Implement retry logic
   - Add monitoring and alerts
   - Write integration tests

3. **Month 2:**
   - Reimplement in Spring Boot + Angular
   - Add PostgreSQL for metadata
   - Add Docker support
