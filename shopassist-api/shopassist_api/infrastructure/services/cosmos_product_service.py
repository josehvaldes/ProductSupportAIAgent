import traceback
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from shopassist_api.application.settings.config import settings
from shopassist_api.application.interfaces.service_interfaces import ProductServiceInterface
from shopassist_api.domain.models.product import Product

class CosmosProductService(ProductServiceInterface):

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
        if settings.cosmosdb_endpoint:
            # Use CosmosDB
            self.client = CosmosClient(
                url=settings.cosmosdb_endpoint,
                credential=DefaultAzureCredential()
            )
            self.cosmosdb_endpoint = settings.cosmosdb_endpoint
            self.database_name = settings.cosmosdb_database
            self.product_container = settings.cosmosdb_product_container
            self.chat_container = settings.cosmosdb_chat_container
        else:
            # No CosmosDB configured
            self.client = None
            self.database_name = None
            self.product_container = None
            self.chat_container = None

    async def get_product_by_id(self, product_id: str)-> Product:
        """Retrieve a product by its ID from CosmosDB."""
        if not self.client or not self.database_name:
            return None

        try:
            # Get a database
            database = self.client.get_database_client(self.database_name)

            # Get the product container
            container = database.get_container_client(self.product_container)
            print(f"Querying for product ID: {product_id} database:{self.database_name}, in container: {self.product_container}")
            # Query for the product by ID
            query = f"SELECT * FROM c WHERE c.id = '{product_id}'"
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            if items:
                return Product(**items[0])
            else:
                return None
        except Exception as e:
            print("An error occurred while retrieving the product:")
            traceback.print_exc()
            return None

    async def search_products_by_category(self, category: str)-> list[Product]:
        """Search products by category from CosmosDB."""
        if not self.client or not self.database_name:
            return []

        try:
            # Get a database
            database = self.client.get_database_client(self.database_name)

            # Get the product container
            container = database.get_container_client(self.product_container)

            # Query for products by category
            query = f"SELECT * FROM c WHERE c.category = '{category}'"
            items = list(container.query_items(
                partition_key=category,
                query=query
                ))
            return items
        except Exception as e:
            print("An error occurred while searching for products:")
            traceback.print_exc()
            return []
        
    async def search_products_by_price_range(self, min_price: float, max_price: float) -> list[Product]:
        """Search products within a price range from CosmosDB."""
        if not self.client or not self.database_name:
            return []

        try:
            # Get a database
            database = self.client.get_database_client(self.database_name)

            # Get the product container
            container = database.get_container_client(self.product_container)

            # Query for products within the price range
            query = f"SELECT * FROM c WHERE c.price >= {min_price} AND c.price <= {max_price}"
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            return items
        except Exception as e:
            print("An error occurred while searching for products by price range:")
            traceback.print_exc()
            return []

    async def health_check_connection(self):
        """Test connection to Azure CosmosDB."""
        if not self.client or not self.database_name:
            print("CosmosDB is not properly configured.")
            return

        try:
            # Get a database
            database = self.client.get_database_client(self.database_name)

            # Create (or get) a container
            container_name = self.product_container
            container = database.get_container_client(container_name)

            query = "SELECT TOP 1 * FROM c"
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            for item in items:
                print(item)


            print("Connected to CosmosDB successfully.")
        except Exception as e:
            print("An error occurred while connecting to CosmosDB:")
            traceback.print_exc()