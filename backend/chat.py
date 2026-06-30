"""LLM integration for chat"""
from typing import List
from langchain_anthropic import ChatAnthropic
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Generate responses using Claude with retrieved context"""
    
    def __init__(self):
        try:
            self.llm = ChatAnthropic(model="claude-sonnet-4-6")
            logger.info("Claude client initialized")
        except Exception as e:
            logger.error(f"Claude init failed: {str(e)}")
            raise
    
    def build_prompt(self, query: str, context_chunks: List[str]) -> str:
        """Construct prompt with context"""
        context = "\n\n".join(context_chunks)
        return f"""Use the following context to answer the question. 
If the answer isn't in the context, say "I don't have that information."

Context:
{context}

Question: {query}

Answer:"""
    
    def chat(self, query: str, context_chunks: List[str]) -> str:
        """Get LLM response with context"""
        try:
            prompt = self.build_prompt(query, context_chunks)
            response = self.llm.invoke(prompt)
            logger.info(f"Generated response for: {query[:50]}")
            return response.content
        except Exception as e:
            logger.error(f"Chat generation failed: {str(e)}")
            raise
