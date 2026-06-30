"""PDF ingestion and embedding pipeline"""
from typing import List, Dict
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process PDFs: extract text, chunk, generate embeddings"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract all text from PDF"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page_num, page in enumerate(reader.pages):
                text += page.extract_text() or ""
            logger.info(f"Extracted {len(text)} chars from PDF")
            return text
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into semantic chunks"""
        chunks = self.splitter.split_text(text)
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Generate embeddings for chunks using OpenAI"""
        try:
            embeddings = self.embeddings.embed_documents(chunks)
            logger.info(f"Generated embeddings for {len(embeddings)} chunks")
            return embeddings
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    def process_document(self, file_path: str) -> Dict:
        """Full pipeline: extract → chunk → embed"""
        logger.info(f"Processing document: {file_path}")
        
        text = self.extract_text_from_pdf(file_path)
        chunks = self.chunk_text(text)
        embeddings = self.generate_embeddings(chunks)
        
        return {
            'text': text,
            'chunks': chunks,
            'embeddings': embeddings,
            'num_chunks': len(chunks)
        }
