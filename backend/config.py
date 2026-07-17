"""Configuration settings"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'rag-index')

# Flask
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
PORT = int(os.getenv('PORT', 5001))

# Rate limits (per client IP; Flask-Limiter limit strings)
RATE_LIMIT_UPLOAD = os.getenv('RATE_LIMIT_UPLOAD', '5 per hour')
RATE_LIMIT_CHAT = os.getenv('RATE_LIMIT_CHAT', '20 per hour')
RATE_LIMIT_SEARCH = os.getenv('RATE_LIMIT_SEARCH', '30 per hour')

# Validation
def validate_config():
    """Ensure all required keys are present"""
    required = ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'PINECONE_API_KEY']
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
