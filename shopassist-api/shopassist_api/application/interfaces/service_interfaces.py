"""
Product service interface for dependency injection.
"""
from abc import ABC, abstractmethod
from typing import List
from shopassist_api.domain.models.product import Product


class ProductServiceInterface(ABC):
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