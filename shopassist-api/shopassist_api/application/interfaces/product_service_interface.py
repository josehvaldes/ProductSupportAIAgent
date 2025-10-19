from abc import ABC, abstractmethod
from typing import Optional

class IProductService(ABC):
    """Interface for product-related operations."""
    
    @abstractmethod
    async def get_product_by_id(self, product_id: str) -> Optional[dict]:
        """Retrieve a product by its ID."""
        pass
    
    @abstractmethod
    async def search_products_by_category(self, category: str) -> list[dict]:
        """Search products by category."""
        pass
    
    @abstractmethod
    async def search_products_by_price_range(self, min_price: float, max_price: float) -> list[dict]:
        """Search products within a price range."""
        pass