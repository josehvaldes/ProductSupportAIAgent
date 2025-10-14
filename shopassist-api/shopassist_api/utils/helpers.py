"""
Utility functions and helpers.
"""
import uuid
import logging
from datetime import datetime
from typing import Any, Dict, Optional


def generate_conversation_id() -> str:
    """Generate a unique conversation ID."""
    return f"conv_{uuid.uuid4().hex[:12]}"


def generate_user_id() -> str:
    """Generate a unique user ID."""
    return f"user_{uuid.uuid4().hex[:12]}"


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format datetime as ISO string."""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input text.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace
    text = " ".join(text.split())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length].rstrip()
    
    return text


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level
        
    Returns:
        Configured logger
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return logging.getLogger(__name__)


def extract_keywords(text: str, min_length: int = 3) -> list[str]:
    """
    Extract keywords from text for search enhancement.
    
    Args:
        text: Input text
        min_length: Minimum keyword length
        
    Returns:
        List of keywords
    """
    import re
    
    # Simple keyword extraction
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter by length and remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'can', 'may', 'might', 'this', 'that', 'these', 'those', 'i', 'you',
        'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    keywords = [
        word for word in words 
        if len(word) >= min_length and word not in stop_words
    ]
    
    return list(set(keywords))  # Remove duplicates
