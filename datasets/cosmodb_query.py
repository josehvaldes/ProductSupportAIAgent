import json
from azure.cosmos import CosmosClient, PartitionKey
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
import traceback

COSMOSDB_ENDPOINT = "https://<accoutname>.documents.azure.com:443/"
COSMOSDB_NAME = "<database_name>"
COSMOSDB_CONTAINER = "products"

def test_cosmosdb_connection():
    """Test connection to Azure CosmosDB."""
    client = CosmosClient(COSMOSDB_ENDPOINT, DefaultAzureCredential())

    # Get a database
    database_name = COSMOSDB_NAME
    database = client.get_database_client(database_name)

    # Create (or get) a container
    container_name = COSMOSDB_CONTAINER
    container = database.get_container_client(container_name)

    query = "SELECT * FROM c"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    for item in items:
        print(item)

    # Query items with a specific filter
    query = "SELECT * FROM c WHERE c.category = 'WirelessUSBAdapters'"
    adapters_items = list(container.query_items(query=query, enable_cross_partition_query=True))
    for item in adapters_items:
        print(item)

if __name__ == "__main__":
    test_cosmosdb_connection()
    print("Connected to CosmosDB successfully.")