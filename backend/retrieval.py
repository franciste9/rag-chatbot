"""Vector search and retrieval"""
from typing import List, Dict
from pinecone import Pinecone
import os
from langchain_openai import OpenAIEmbeddings
import logging

logger = logging.getLogger(__name__)


class RetrieverService:
    """Search and retrieve relevant chunks from Pinecone"""
    
    def __init__(self):
        try:
            self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            self.index = self.pc.Index(os.getenv('PINECONE_INDEX_NAME'))
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            logger.info("Pinecone client initialized")
        except Exception as e:
            logger.error(f"Pinecone init failed: {str(e)}")
            raise
    
    def store_chunks(self, chunks: List[str], embeddings: List[List[float]], doc_id: str) -> None:
        """Store chunks and embeddings in Pinecone"""
        try:
            vectors_to_upsert = [
                (f"{doc_id}_{i}", emb, {
                    "chunk_text": chunk,
                    "doc_id": doc_id,
                    "chunk_index": i
                })
                for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
            ]

            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                self.index.upsert(vectors=vectors_to_upsert[i:i + batch_size])
            logger.info(f"Stored {len(vectors_to_upsert)} vectors for doc {doc_id}")
        except Exception as e:
            logger.error(f"Storage failed: {str(e)}")
            raise
    
    def search(self, query: str, top_k: int = 5, doc_id: str = None) -> List[Dict]:
        """Search for relevant chunks, optionally scoped to a single document"""
        try:
            query_embedding = self.embeddings.embed_query(query)
            query_kwargs = {
                'vector': query_embedding,
                'top_k': top_k,
                'include_metadata': True
            }
            if doc_id:
                query_kwargs['filter'] = {'doc_id': {'$eq': doc_id}}
            results = self.index.query(**query_kwargs)
            
            retrieved = [
                {
                    'text': match.metadata.get('chunk_text', ''),
                    'score': match.score,
                    'doc_id': match.metadata.get('doc_id', 'unknown'),
                    'chunk_index': match.metadata.get('chunk_index', -1)
                }
                for match in results.matches
            ]
            
            logger.info(f"Retrieved {len(retrieved)} chunks for query: {query[:50]}")
            return retrieved
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise
