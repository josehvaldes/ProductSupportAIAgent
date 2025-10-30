import traceback
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from shopassist_api.application.settings.config import settings
from shopassist_api.application.interfaces.service_interfaces import RepositoryServiceInterface
from shopassist_api.domain.models.product import Product

class DumpProductService(RepositoryServiceInterface):

    def __init__(self):
        self.client = None
        self.model = None
        self.database_name = None
        self.cosmosdb_endpoint = None
        self.product_container = None
        self.chat_container = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the CosmosDB client based on configuration."""
        pass

    async def get_product_by_id(self, product_id: str)-> Product:
        """Retrieve a product by its ID from CosmosDB."""

        product:Product = { "id": product_id,
                    "name": "Test Product",
                    "description": "A product for testing", 
                    "category": "Testing", 
                    "price": "19.99", 
                    "brand": "TestBrand", 
                    "rating": "4.5", 
                    "review_count": "10", 
                    "product_url": "http://example.com/product/test123", 
                    "image_url": "http://example.com/product/test123/image.jpg",  
                    "category_full": ["Smartphones","Testing","Unit Tests"], 
                    "availability": "In Stock" }
        return Product(**product)
    
    async def search_products_by_category(self, category: str) -> list[Product]:
        """Search products by category."""
        products = []
        for i in range(3):
            product:Product = { "id": f"test{i}",
                        "name": f"Test Product {i}",
                        "description": "A product for testing", 
                        "category": category, 
                        "price": f"{19.99 + i}", 
                        "brand": "TestBrand", 
                        "rating": "4.5", 
                        "review_count": "10", 
                        "product_url": f"http://example.com/product/test{i}", 
                        "image_url": f"http://example.com/product/test{i}/image.jpg",  
                        "category_full": ["Smartphones","Testing","Unit Tests"], 
                        "availability": "In Stock" }
            products.append(Product(**product))
        return products
    
    async def search_products_by_price_range(self, min_price: float, max_price: float) -> list[Product]:
        """Search products within a price range."""
        products = []
        for i in range(4):
            price = min_price + (i * (max_price - min_price) / 4)
            product:Product = { "id": f"test{i}",
                        "name": f"Test Product {i}",
                        "description": "A product for testing", 
                        "category": "Testing", 
                        "price": f"{price}", 
                        "brand": "TestBrand", 
                        "rating": "4.5", 
                        "review_count": "10", 
                        "product_url": f"http://example.com/product/test{i}", 
                        "image_url": f"http://example.com/product/test{i}/image.jpg",  
                        "category_full":["Smartphones","Testing","Unit Tests"], 
                        "availability": "In Stock" }
            products.append(Product(**product))
        return products
    
    async def search_products_by_text(self, text: str) -> list[dict[str, any]]:
        """Search products by description."""
        products = []
        for i in range(2):
            product:Product = { "id": f"test{i}",
                        "name": f"Test Product {i}",
                        "description": "A product for testing with " + text, 
                        "category": "Testing", 
                        "price": f"{19.99 + i}", 
                        "brand": "testbrand", 
                        "rating": "4.5", 
                        "review_count": "10", 
                        "product_url": f"http://example.com/product/test{i}", 
                        "image_url": f"http://example.com/product/test{i}/image.jpg",  
                        "category_full": ["Smartphones","Testing","Unit Tests"], 
                        "availability": "In Stock" }
            products.append(Product(**product))
        return products
    
    async def search_products_by_name(self, name: str) -> list[dict[str, any]]:
        """Search products by name."""
        products = []
        for i in range(2):
            product:Product = { "id": f"test{i}",
                        "name": name,
                        "description": "A product for testing", 
                        "category": "Testing", 
                        "price": f"{19.99 + i}", 
                        "brand": "TestBrand", 
                        "rating": "4.5", 
                        "review_count": "10", 
                        "product_url": f"http://example.com/product/test{i}", 
                        "image_url": f"http://example.com/product/test{i}/image.jpg",  
                        "category_full": ["Smartphones","Testing","Unit Tests"], 
                        "availability": "In Stock" }
            products.append(Product(**product))
        return products
    
    async def get_conversation_history(self, session_id: str) -> list[dict[str, any]]:
        """Get conversation history for a session"""
        history = [
            {
                "session_id": session_id,
                "user_id": "user123",
                "role": "user",
                "content": "Hello, I need help with a product.",
                "timestamp": "2024-01-01T12:00:00Z",
                "metadata": {}
            },
            {
                "session_id": session_id,
                "user_id": "agent456",
                "role": "agent",
                "content": "Sure, what product do you need help with?",
                "timestamp": "2024-01-01T12:01:00Z",
                "metadata": {}
            }
        ]
        return history
    async def save_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        timestamp: str,
        metadata: dict = None 
    ):
        """Save a message to the conversation history"""
        print(f"Saving message to session {session_id}: [{role}] {content} at {timestamp}")
        return