"""
Product service interface for dependency injection.
"""
from abc import ABC, abstractmethod
from typing import List
from shopassist_api.domain.models.product import Product


class ProductServiceInterface(ABC):
    """Abstract base class for product service implementations."""
    
    @abstractmethod
    async def get_product_by_id(self, product_id: str) -> Product:
        """Retrieve a product by its ID."""
        pass
    
    @abstractmethod
    async def search_products_by_category(self, category: str) -> List[Product]:
        """Search products by category."""
        pass
    
    @abstractmethod
    async def search_products_by_price_range(self, min_price: float, max_price: float) -> List[Product]:
        """Search products within a price range."""
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