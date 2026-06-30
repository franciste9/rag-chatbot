"""Utility functions"""
import logging

logger = logging.getLogger(__name__)


def setup_logging(level=logging.INFO):
    """Configure logging"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def format_search_result(result):
    """Format a search result for display"""
    return {
        'text': result.get('text', ''),
        'score': round(result.get('score', 0), 4),
        'source': result.get('doc_id', 'unknown')
    }
