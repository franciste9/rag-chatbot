#!/usr/bin/env python3
"""Test Chat endpoint with retrieval and Claude integration"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv()

from ingestion import DocumentProcessor
from retrieval import RetrieverService
from chat import ChatService
import uuid
import time

print("\n" + "="*60)
print("CHAT ENDPOINT TEST")
print("="*60)

# Initialize services
print("\nInitializing services...")
try:
    processor = DocumentProcessor()
    retriever = RetrieverService()
    chat = ChatService()
    print("✅ All services initialized")
except Exception as e:
    print(f"❌ Initialization failed: {str(e)}")
    sys.exit(1)

# Process sample PDF
print("\nProcessing sample PDF...")
pdf_path = "/Users/francis.te/Github/rag-chatbot/sample5pages.pdf"
try:
    result = processor.process_document(pdf_path)
    doc_id = str(uuid.uuid4())
    retriever.store_chunks(result['chunks'], result['embeddings'], doc_id)
    print(f"✅ PDF processed and stored ({result['num_chunks']} chunks)")
except Exception as e:
    print(f"❌ PDF processing failed: {str(e)}")
    sys.exit(1)

# Test chat queries
test_queries = [
    "What documents are mentioned in this file?",
    "What are the main topics covered?",
    "Summarize the key information",
]

print("\n" + "="*60)
print("TESTING CHAT QUERIES")
print("="*60)

for i, query in enumerate(test_queries, 1):
    print(f"\n{'─'*60}")
    print(f"Query {i}: {query}")
    print('─'*60)

    try:
        # Retrieve context
        start_retrieval = time.time()
        search_results = retriever.search(query, top_k=5)
        retrieval_time = time.time() - start_retrieval

        print(f"✅ Retrieved {len(search_results)} chunks ({retrieval_time:.2f}s)")
        print(f"\nContext chunks:")
        for j, chunk in enumerate(search_results[:2], 1):
            preview = chunk['text'][:100].replace('\n', ' ')
            print(f"  {j}. Score: {chunk['score']:.3f} | {preview}...")

        # Generate chat response
        context_chunks = [r['text'] for r in search_results]
        start_chat = time.time()
        answer = chat.chat(query, context_chunks)
        chat_time = time.time() - start_chat

        print(f"\n✅ Generated response ({chat_time:.2f}s)")
        print(f"\nAnswer:")
        print(f"  {answer}")

        # Check if answer references context
        if "don't have" in answer.lower() or "not found" in answer.lower():
            print("\n⚠️  Answer indicates no relevant information found")
        else:
            print("\n✅ Answer generated from context")

    except Exception as e:
        print(f"❌ Chat failed: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("✅ Chat endpoint test completed")
print("\nVerify:")
print("  1. Answers are grounded in retrieved chunks")
print("  2. No hallucinations (answers match document content)")
print("  3. Response times are < 5 seconds")
print("  4. Claude properly uses context for grounding")
print("="*60 + "\n")
