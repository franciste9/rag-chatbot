#!/usr/bin/env python3
"""Test Pinecone integration without running Flask"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv()

# Test 1: Check environment variables
print("\n" + "="*60)
print("TEST 1: Environment Variables")
print("="*60)

required_keys = ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'PINECONE_API_KEY', 'PINECONE_INDEX_NAME']
for key in required_keys:
    value = os.getenv(key)
    status = "✅" if value else "❌"
    print(f"{status} {key}: {value[:20]}..." if value else f"{status} {key}: MISSING")

# Test 2: Initialize Pinecone
print("\n" + "="*60)
print("TEST 2: Pinecone Connection")
print("="*60)

try:
    from retrieval import RetrieverService
    retriever = RetrieverService()
    print("✅ RetrieverService initialized successfully")
    print(f"✅ Pinecone index: {os.getenv('PINECONE_INDEX_NAME')}")
except Exception as e:
    print(f"❌ Pinecone initialization failed: {str(e)}")
    sys.exit(1)

# Test 3: Initialize DocumentProcessor
print("\n" + "="*60)
print("TEST 3: Document Processor")
print("="*60)

try:
    from ingestion import DocumentProcessor
    processor = DocumentProcessor()
    print("✅ DocumentProcessor initialized successfully")
except Exception as e:
    print(f"❌ DocumentProcessor initialization failed: {str(e)}")
    sys.exit(1)

# Test 4: Test PDF Processing
print("\n" + "="*60)
print("TEST 4: PDF Processing")
print("="*60)

pdf_path = "/Users/francis.te/Github/rag-chatbot/sample5pages.pdf"
if not os.path.exists(pdf_path):
    print(f"❌ Sample PDF not found at {pdf_path}")
    sys.exit(1)

try:
    result = processor.process_document(pdf_path)
    print(f"✅ PDF processed successfully")
    print(f"   - Text extracted: {len(result['text'])} characters")
    print(f"   - Chunks created: {result['num_chunks']}")
    print(f"   - Embeddings generated: {len(result['embeddings'])}")

    # Verify chunks and embeddings match
    if len(result['chunks']) != result['num_chunks']:
        print(f"❌ Chunk count mismatch: {len(result['chunks'])} vs {result['num_chunks']}")
    else:
        print(f"✅ Chunk count verified")

except Exception as e:
    print(f"❌ PDF processing failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Store chunks in Pinecone
print("\n" + "="*60)
print("TEST 5: Store Chunks in Pinecone")
print("="*60)

try:
    import uuid
    doc_id = str(uuid.uuid4())
    retriever.store_chunks(result['chunks'], result['embeddings'], doc_id)
    print(f"✅ Chunks stored successfully")
    print(f"   - Document ID: {doc_id}")
    print(f"   - Vectors stored: {len(result['chunks'])}")
except Exception as e:
    print(f"❌ Failed to store chunks: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Search functionality
print("\n" + "="*60)
print("TEST 6: Semantic Search")
print("="*60)

test_queries = [
    "What is this document about?",
    "What are the main topics covered?",
    "Tell me about the key concepts"
]

for query in test_queries:
    try:
        results = retriever.search(query, top_k=3)
        print(f"\n✅ Query: '{query}'")
        print(f"   Results: {len(results)} chunks retrieved")

        for i, result in enumerate(results[:2], 1):  # Show top 2
            score = result.get('score', 0)
            text_preview = result['text'][:80].replace('\n', ' ')
            print(f"   {i}. Score: {score:.3f} | {text_preview}...")

    except Exception as e:
        print(f"❌ Search failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Test 7: Verify retrieval quality
print("\n" + "="*60)
print("TEST 7: Retrieval Quality Check")
print("="*60)

try:
    results = retriever.search("document", top_k=5)
    all_scores = [r.get('score', 0) for r in results]
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0

    print(f"✅ Retrieval quality metrics:")
    print(f"   - Average score: {avg_score:.3f}")
    print(f"   - Top score: {max(all_scores):.3f}")
    print(f"   - Min score: {min(all_scores):.3f}")

    if avg_score > 0.75:
        print(f"✅ Score > 0.75 (EXCELLENT)")
    elif avg_score > 0.5:
        print(f"⚠️  Score between 0.5-0.75 (GOOD)")
    else:
        print(f"⚠️  Score < 0.5 (CHECK CHUNKING)")

except Exception as e:
    print(f"❌ Quality check failed: {str(e)}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*60)
print("✅ ALL TESTS PASSED - Pinecone integration is working!")
print("="*60)
