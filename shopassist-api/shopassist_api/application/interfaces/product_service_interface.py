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
