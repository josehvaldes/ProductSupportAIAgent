import traceback
from datetime import datetime
from typing import List, Dict
import uuid
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from langsmith import traceable
from shopassist_api.application.settings.config import settings
from shopassist_api.application.interfaces.service_interfaces import RepositoryServiceInterface
from shopassist_api.domain.models.message import Message
from shopassist_api.domain.models.session_context import SessionContext
from shopassist_api.domain.models.user_preferences import UserPreferences
from shopassist_api.logging_config import get_logger
from shopassist_api.infrastructure.services.azure_credential_manager import get_credential_manager

logger = get_logger(__name__)

class CosmosProductService(RepositoryServiceInterface):

    def __init__(self):
        self.client = None
        self.database_name = None
        self.product_container = None
        self.chat_container = None
        self.session_container = None
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
            self.messages_container = settings.cosmosdb_messages_container
            self.session_container = settings.cosmosdb_session_container

            self.database = self.client.get_database_client(self.database_name)

        else:
            self.client = None

    @traceable(name="cosmos.get_product_by_id", tags=["cosmos", "product", "azure"], metadata={"version": "1.0"})
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
    
    @traceable(name="cosmos.get_products_by_ids", tags=["cosmos", "product", "azure"], metadata={"version": "1.0"})
    async def get_products_by_ids(self, product_ids: List[str]) -> list[dict[str, any]]:
        """Retrieve multiple products by their IDs from CosmosDB."""
        if not self.client or not self.database_name:
            return []
        
        if not product_ids or len(product_ids) == 0:
                return []
        try:
            # Get the product container
            container = self.database.get_container_client(self.product_container)
            # Query for products by IDs
            ids_string = ",".join([f"'{pid}'" for pid in product_ids])
            query = f"SELECT * FROM c WHERE c.id IN ({ids_string})"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
                ))
            return items
        except Exception as e:
            logger.error(f"Error retrieving products by IDs: {e}")
            traceback.print_exc()
            return []

    @traceable(name="cosmos.search_products_by_category", tags=["cosmos", "product", "azure"], metadata={"version": "1.0"})
    async def search_products_by_category(self, category: str)-> list[dict[str, any]]:
        """Search products by category from CosmosDB."""
        if not self.client or not self.database:
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
    
    @traceable(name="cosmos.search_products_by_text", tags=["cosmos", "product", "azure"], metadata={"version": "1.0"})
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
    
    @traceable(name="cosmos.search_products_by_name", tags=["cosmos", "product", "azure"], metadata={"version": "1.0"})
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
        

    @traceable(name="cosmos.get_conversation_history", tags=["cosmos", "history", "azure"], metadata={"version": "1.0"})
    async def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        try:
            
            container = self.database.get_container_client(self.messages_container)
            
            query = """
            SELECT c.role, c.content, c.timestamp, c.metadata, c.id, c.user_id, c.session_id
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
            container = self.database.get_container_client(self.messages_container)
            
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
    
    async def create_session(self, data: SessionContext) -> str:
        """Create a new session and return its ID"""
        try:
            if data is None:
                raise ValueError("SessionContext data must be provided to create a session.")
            
            if data.id is None:
                data.id = str(uuid.uuid4())

            logger.info(f"Created new session with ID: {data.id}")
            container = self.database.get_container_client(self.session_container)
            safe_data = data.model_dump(mode='json') if data else {}
            print(safe_data)
            container.create_item(body=safe_data)
            logger.info(f"Saved session context for session ID: {data.id}")
            
            return data.id
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            traceback.print_exc()
            return None
    
    async def get_session(self, session_id: str) -> SessionContext:
        """Retrieve session details by session ID"""
        try:
            logger.info(f"Retrieving session with ID: {session_id}")
            container = self.database.get_container_client(self.session_container)
            query = """
            SELECT *
            FROM c
            WHERE c.id = @id
            """
            items = list(container.query_items(
                query=query,
                parameters=[{"name": "@id", "value": session_id}],
                enable_cross_partition_query=True
            ))
            if items:
                session_data = items[0]
                # Convert to SessionContext model if needed
                session = SessionContext(**session_data)

                messages = await self.get_conversation_history(session_id)
                session.messages = [ Message.model_validate(msg) for msg in messages ]
                return session
            else:
                logger.info(f"No session found with ID: {session_id}")
                return None
        except Exception as e:
            logger.error(f"Error retrieving session: {e}")
            traceback.print_exc()
            return None
        
    async def delete_session(self, user_id:str, session_id: str) -> None:
        """Delete a session by session ID"""
        try:
            container = self.database.get_container_client(self.session_container)
            # delete the session item without retrieving it first
            container.delete_item(item=session_id, partition_key=user_id)
        except CosmosResourceNotFoundError:
            logger.warning(f"Session with ID: {session_id}, User Id {user_id}, not found for deletion.")
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            traceback.print_exc()

    async def get_preferences(
        self, 
        session_id: str
    ) -> UserPreferences:
        """Get user preferences for a session"""
        try:
            session = await self.get_session(session_id)
            if session and session.user_preferences:
                preferences = UserPreferences.model_validate(session.user_preferences)
                return preferences
            else:
                logger.info(f"No user preferences found for session ID: {session_id}")
                return None
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            traceback.print_exc()
            return None
        
    async def update_preferences(
        self, 
        session_id: str, 
        preferences: UserPreferences
    ) -> None:
        """Update user preferences for a session"""
        try:
            container = self.database.get_container_client(self.session_container)
            # Retrieve existing session
            session = await self.get_session(session_id)
            if not session:
                logger.error(f"Session ID {session_id} not found for updating preferences.")
                return
            
            # Update preferences
            session.user_preferences = preferences
            safe_data = SessionContext.model_dump(session)
            container.upsert_item(body=safe_data)
            logger.info(f"Updated user preferences for session ID: {session_id}")
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            traceback.print_exc()