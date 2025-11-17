import traceback
import uuid
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from shopassist_api.application.settings.config import settings
from shopassist_api.application.interfaces.service_interfaces import RepositoryServiceInterface
from shopassist_api.domain.models.product import Product
from shopassist_api.domain.models.session_context import SessionContext
from shopassist_api.domain.models.user_preferences import UserPreferences
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

class DumbProductService(RepositoryServiceInterface):

    def __init__(self):
        self.client = None
        self.model = None
        self.database_name = None
        self.cosmosdb_endpoint = None
        self.product_container = None
        self.category_container = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the CosmosDB client based on configuration."""
        pass

    async def get_product_by_id(self, product_id: str)-> dict[str, any]:
        """Retrieve a product by its ID from CosmosDB."""

        return { "id": product_id,
                    "name": "Test Product",
                    "description": "A product for testing", 
                    "category": "Testing", 
                    "price": 19.99, 
                    "brand": "TestBrand", 
                    "rating": "4.5", 
                    "review_count": "10", 
                    "product_url": "http://example.com/product/test123", 
                    "image_url": f"https://m.media-amazon.com/images/I/41gikeSuhAL._SY300_SX300_QL70_FMwebp_.jpg",
                    "category_full": "Smartphones > Testing > Unit Tests", 
                    "availability": "In Stock" }
    
    async def get_products_by_ids(self, product_ids):
        return [await self.get_product_by_id(pid) for pid in product_ids]
    
    async def search_products_by_category(self, category: str)-> list[dict[str, any]]:
        """Search products by category."""
        products = []
        for i in range(3):
            products.append( { "id": f"test{i}",
                        "name": f"Test Product {i}",
                        "description": "A product for testing", 
                        "category": category, 
                        "price": f"{19.99 + i}", 
                        "brand": "TestBrand", 
                        "rating": "4.5", 
                        "review_count": "10", 
                        "product_url": f"http://example.com/product/test{i}", 
                        "image_url": f"https://m.media-amazon.com/images/I/41gikeSuhAL._SY300_SX300_QL70_FMwebp_.jpg",  
                        "category_full": "Smartphones > Testing > Unit Tests", 
                        "availability": "In Stock" }
                        )

        return products
    
    async def search_products_by_price_range(self, min_price: float, max_price: float) -> list[dict[str, any]]:
        """Search products within a price range."""
        products = []
        for i in range(4):
            price = min_price + (i * (max_price - min_price) / 4)
            products.append( { "id": f"test{i}",
                        "name": f"Test Product {i}",
                        "description": "A product for testing", 
                        "category": "Testing", 
                        "price": f"{price}", 
                        "brand": "TestBrand", 
                        "rating": "4.5", 
                        "review_count": "10", 
                        "product_url": f"http://example.com/product/test{i}", 
                        "image_url": f"https://m.media-amazon.com/images/I/41gikeSuhAL._SY300_SX300_QL70_FMwebp_.jpg",  
                        "category_full":"Smartphones > Testing > Unit Tests", 
                        "availability": "In Stock" }
            )
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
                        "image_url": "https://m.media-amazon.com/images/I/31dJ+lXJq3L._SY300_SX300_.jpg",  
                        "category_full": "Smartphones > Testing > Unit Tests", 
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
                        "image_url": "https://m.media-amazon.com/images/I/31dJ+lXJq3L._SY300_SX300_.jpg",
                        "category_full": "Smartphones > Testing > Unit Tests", 
                        "availability": "In Stock" }
            products.append(Product(**product))
        return products
    
    async def get_conversation_history(self, session_id: str) -> list[dict[str, any]]:

        """Get conversation history for a session"""
        history = []
        if session_id == "58ca3bbb-1fbc-4cfa":
            history = [
            {
                "id": "msg1",
                "user_id": "default_user",
                "session_id": session_id,
                "role": "user",
                "content": ".I need a printer under 100 USD",
                "timestamp": "2025-10-30T20:44:28.195142+00:00",
                "metadata": {}
            },
            {
                "id": "msg1",
                "user_id": "default_user",
                "session_id": session_id,
                "role": "assistant",
                "content": ".You can find good printers under $100. Here are two options:\n\n1. **HP Deskjet 2723 AIO Printer**  \n   - Price: $77.05  \n   - Features: Print, copy, scan with WiFi and Bluetooth connectivity; Up to 1200 x 1200 DPI resolution; 60-sheet input tray, ideal for home use.\n\n2. **Canon PIXMA E477 All-in-One Wireless Ink Efficient Colour Printer**  \n   - Price: $69.91  \n   - Features: Print, scan, copy with WiFi and USB; High print resolution up to 4800 x 600 dpi; \n\nWould you like details on warranty, ink cartridges, or setup for either printer?",
                "timestamp": "2025-10-30T20:44:28.441405+00:00",
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
        logger.info(f"Saving message to session {session_id}: [{role}] {content} at {timestamp}")
        return

    async def health_check(self) -> bool:
        """Ping the service to check connectivity"""
        return True
    
    async def create_session(self, data = None):
        return str(uuid.uuid4())
    
    async def get_session(self, session_id: str)-> SessionContext:
        return SessionContext( **{"id": session_id, 
                                  "user_id": "test_user",
                                    "created_at": "2025-10-30T20:44:28.195142+00:00",
                                    "updated_at": "2025-10-30T20:44:28.195142+00:00",
                                    "messages": [],
                                    "user_preferences": None,
                                    "current_intent": None,
                                    "metadata": {
                                        "user_agent": "DumbAgent/1.0",
                                        "products": [
                                            {
                                                "id": "prod123",
                                                "name": "Test Product 123",
                                                "category": "Testing",
                                                "price": 99.99,
                                                "description": "A sample product for testing purposes."
                                            },
                                            {
                                                "id": "prod456",
                                                "name": "Test Product 456",
                                                "category": "Testing",
                                                "price": 149.99,
                                                "description": "Another sample product for testing purposes."
                                            }
                                        ]
                                    }
                                  } )
    
    async def delete_session(self, user_id:str, session_id: str) -> None:
        """Delete a session by session ID"""
        logger.info(f"Deleting session {session_id} for user {user_id}")
        return None
    
    async def get_preferences(self, session_id)-> UserPreferences:
        return UserPreferences( **{"session_id": session_id, 
                                   "preferences": {
                                        "price_range": (50.0, 150.0),
                                        "preferred_categories": ["Electronics", "Books"],
                                        "preferred_brands": ["BrandA", "BrandB"],
                                        "mentioned_products": ["prod123", "prod456"]

        }} )
    
    async def update_preferences(self, session_id: str, preferences: dict) -> None:
        """Update user preferences for a session"""
        logger.info(f"Updating preferences for session {session_id}: {preferences}")
        return None
