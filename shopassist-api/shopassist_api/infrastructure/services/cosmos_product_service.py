import traceback
from datetime import datetime
from typing import List, Dict
import uuid
from azure.cosmos import CosmosClient
from shopassist_api.application.settings.config import settings
from shopassist_api.application.interfaces.service_interfaces import RepositoryServiceInterface
from shopassist_api.logging_config import get_logger
from shopassist_api.infrastructure.services.azure_credential_manager import get_credential_manager

logger = get_logger(__name__)

class CosmosProductService(RepositoryServiceInterface):

    def __init__(self):
        self.client = None
        self.database_name = None
        self.product_container = None
        self.chat_container = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the CosmosDB client based on configuration."""
        if settings.cosmosdb_endpoint:
            # Use shared credential manager
            credential_manager = get_credential_manager()
            credential = credential_manager.get_cosmos_credential()
            
            self.client = CosmosClient(
                url=settings.cosmosdb_endpoint,
                credential=credential
            )
            self.database_name = settings.cosmosdb_database
            self.product_container = settings.cosmosdb_product_container
            self.chat_container = settings.cosmosdb_chat_container

            self.database = self.client.get_database_client(self.database_name)

        else:
            self.client = None

    async def get_product_by_id(self, product_id: str)-> dict[str, any]:
        """Retrieve a product by its ID from CosmosDB."""
        if not self.client or not self.database_name:
            return None

        try:

            # Get the product container
            container = self.database.get_container_client(self.product_container)
            logger.info(f"Querying for product ID: {product_id} database:{self.database_name}, in container: {self.product_container}")
            # Query for the product by ID
            query = f"SELECT * FROM c WHERE c.id = '{product_id}'"
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            if items:
                return items[0]
            else:
                return None
        except Exception as e:
            logger.error(f"Error retrieving product by ID: {e}")
            traceback.print_exc()
            return None

    async def search_products_by_category(self, category: str)-> list[dict[str, any]]:
        """Search products by category from CosmosDB."""
        if not self.client or not self.database_name:
            return []

        try:
            # Get the product container
            container = self.database.get_container_client(self.product_container)

            # Query for products by category
            query = f"SELECT * FROM c WHERE c.category = '{category}'"
            items = list(container.query_items(
                partition_key=category,
                query=query
                ))
            return items
        except Exception as e:
            logger.error(f"Error searching products by category: {e}")
            traceback.print_exc()
            return []
        
    async def search_products_by_price_range(self, min_price: float, max_price: float) -> list[dict[str, any]]:
        """Search products within a price range from CosmosDB."""
        if not self.client or not self.database_name:
            return []

        try:

            # Get the product container
            container = self.database.get_container_client(self.product_container)

            # Query for products within the price range
            query = f"SELECT * FROM c WHERE c.price >= {min_price} AND c.price <= {max_price}"
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            return items
        except Exception as e:
            logger.error(f"Error searching products by price range: {e}")
            traceback.print_exc()
            return []

    async def search_products_by_text(self, text: str) -> list[dict[str, any]]:
        """Search products by text from CosmosDB."""
        if not self.client or not self.database_name:
            return []

        try:
            # Get the product container
            container = self.database.get_container_client(self.product_container)

            # Query for products by text in name or description
            query = f"SELECT * FROM c WHERE CONTAINS(c.name, '{text}') OR CONTAINS(c.description, '{text}')"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
                ))
            return items
        except Exception as e:
            logger.error(f"Error searching products by text: {e}")
            traceback.print_exc()
            return []
    
    async def search_products_by_name(self, name: str) -> list[dict[str, any]]:
        """Search products by name from CosmosDB."""
        if not self.client or not self.database_name:
            return []

        try:
            
            # Get the product container
            container = self.database.get_container_client(self.product_container)

            # Query for products by name
            query = f"SELECT * FROM c WHERE CONTAINS(c.name, '{name}')"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
                ))
            return items
        except Exception as e:
            logger.error(f"Error searching products by name: {e}")
            traceback.print_exc()
            return []
        


    async def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        try:
            
            container = self.database.get_container_client("sessions")
            
            query = """
            SELECT c.role, c.content, c.timestamp
            FROM c
            WHERE c.session_id = @session_id
            ORDER BY c.timestamp ASC
            """
            logger.info(f"Getting conversation history for session_id: {session_id}")
            items = list(container.query_items(
                query=query,
                parameters=[{"name": "@session_id", "value": session_id}],
                enable_cross_partition_query=True
            ))
            
            return items
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    async def save_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        timestamp: datetime,
        metadata: Dict = None
    ):
        """Save a message to conversation history"""
        try:
            container = self.database.get_container_client("sessions")
            
            message = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": session_id,
                "role": role,
                "content": content,
                "timestamp": timestamp.isoformat(),
                "metadata": metadata or {}
            }
            
            container.create_item(body=message)
            logger.info(f"Saved message for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise
    
    
    async def health_check(self) -> bool:
        """Ping the service to check connectivity"""
        """Test connection to Azure CosmosDB."""
        """health_check_connection"""
        if not self.client or not self.database_name:
            logger.error("CosmosDB client not initialized.")
            return False
        try:
            # Create (or get) a container
            container_name = self.product_container
            container = self.database.get_container_client(container_name)

            # query = "SELECT TOP 1 * FROM c"
            # items = list(container.query_items(query=query, enable_cross_partition_query=True))
            logger.info("Connected to CosmosDB successfully.")
            return True
        except Exception as e:
            logger.error(f"Error connecting to CosmosDB: {e}")
            traceback.print_exc()
            return False