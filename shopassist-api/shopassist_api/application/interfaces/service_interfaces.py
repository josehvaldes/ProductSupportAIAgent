"""
Product service interface for dependency injection.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Generator
from datetime import datetime

from shopassist_api.domain.models.session_context import SessionContext
from shopassist_api.domain.models.user_preferences import UserPreferences

class RepositoryServiceInterface(ABC):
    """Abstract base class for product service implementations."""
    
    @abstractmethod
    async def get_product_by_id(self, product_id: str) -> dict[str, any]:
        """Retrieve a product by its ID."""
        pass
    
    @abstractmethod
    async def search_products_by_category(self, category: str) -> List[dict[str, any]]:
        """Search products by category."""
        pass
    
    @abstractmethod
    async def search_products_by_price_range(self, min_price: float, max_price: float) -> List[dict[str, any]]:
        """Search products within a price range."""
        pass

    @abstractmethod
    async def search_products_by_text(self, text: str) -> List[dict[str, any]]:
        """Search products by brand."""
        pass

    @abstractmethod
    async def search_products_by_name(self, name: str) -> List[dict[str, any]]:
        """Search products by name."""
        pass
    @abstractmethod
    async def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        pass
    
    async def create_session(self, data: SessionContext = None) -> str:
        """Create a new session and return its ID"""
        pass

    async def get_session(self, session_id: str) -> SessionContext:
        """Retrieve session details by session ID"""
        pass

    async def delete_session(self, user_id:str, session_id: str) -> None:
        """Delete a session by session ID"""
        pass

    async def update_preferences(
        self, 
        session_id: str, 
        preferences: dict
    ) -> None:
        """Update user preferences for a session"""
        pass

    async def get_preferences(
        self, 
        session_id: str
    ) -> UserPreferences:
        """Get user preferences for a session"""
        pass

    
    @abstractmethod
    async def save_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        timestamp: datetime,
        metadata: Dict = None 
    ):
        """Save a message to the conversation history"""
        pass

    async def health_check(self) -> bool:
        """Ping the service to check connectivity"""
        pass

class EmbeddingServiceInterface(ABC):
    """Abstract base class for embedding service implementations."""
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in the given text."""
        pass

    @abstractmethod
    def generate_embedding(self, input_text: str) -> list[float]:
        """Generate embedding for the given input text."""
        pass
    
    @abstractmethod
    def generate_embedding_batch(self, input_texts: list[str], batch_size: int = 50) -> list[dict]:
        """Generate embeddings for a list of input texts."""
        pass
    async def health_check(self) -> bool:
        """Ping the service to check connectivity"""
        pass


class VectorServiceInterface(ABC):
    """Abstract base class for Milvus service implementations."""
    
    @abstractmethod
    def insert_products(self, products: List[dict]) -> int:
        """Insert product embeddings into Milvus."""
        pass
    
    @abstractmethod
    def insert_knowledge_base(self, chunks: List[dict]) -> int:
        """Insert knowledge base chunks into Milvus."""
        pass
    @abstractmethod
    def insert_categories(self, categories: List[dict]) -> int:
        """Insert category embeddings into Milvus."""
        pass
    
    @abstractmethod
    def search_products(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: str = None
    ) -> List[dict]:
        """Search products by vector similarity."""
        pass
    
    @abstractmethod
    def search_knowledge_base(
        self,
        query_embedding: List[float],
        top_k: int = 3
    ) -> List[dict]:
        """Search knowledge base chunks by vector similarity."""
        pass

    def search_categories(
        self,query_embedding: List[float],
        top_k: int = 5) -> List[Dict]:
        """Search categories by vector similarity."""
        pass
            
    async def health_check(self) -> bool:
        """Ping the service to check connectivity"""
        pass


class LLMServiceInterface(ABC):
    """Abstract base class for LLM service implementations."""
    
    @abstractmethod
    def generate_response(
        self,
        messages: List[dict],
        temperature: float = 0.3,
        max_tokens: int = 500
    ) -> Dict:
        """Generate a response from the LLM."""
        pass
    @abstractmethod
    def streaming_response(
        self,
        messages: List[dict],
        temperature: float = 0.3,
        max_tokens: int = 500
    )-> Generator[str, None, None]:
        """Generate a streaming response from the LLM."""
        pass
    @abstractmethod
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        pass

    async def health_check(self) -> bool:
        """Ping the service to check connectivity"""
        pass


class CacheServiceInterface(ABC):
    """Abstract base class for Cache service implementations."""
    
    @abstractmethod
    async def get(self, key: str) -> str:
        """Retrieve a value from the cache by key."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str, ttl: int = None) -> None:
        """Set a value in the cache with an optional expiration time."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a value from the cache by key."""
        pass

    async def health_check(self) -> bool:
        """Ping the service to check connectivity"""
        pass