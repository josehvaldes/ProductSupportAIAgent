import json
from azure.cosmos import CosmosClient, PartitionKey
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
import traceback

COSMOSDB_ENDPOINT = "https://<accoutname>.documents.azure.com:443/"
COSMOSDB_NAME = "<database_name>"
COSMOSDB_CONTAINER = "products"

def transform_document_body(data:dict) -> dict:
    """Generate a sample document body."""
    return {
        "id": data.get("id", ""),
        "name": data.get("name", ""),
        "description": data.get("description", ""),
        "category": data.get("category", ""),
        "category_full": data.get("category_full", []),
        "price": data.get("price", 0.0),
        "brand": data.get("brand", ""),
        "rating": data.get("rating", 0.0),
        "review_count": data.get("review_count", 0.0),
        "chunks": [ chunk for chunk in data.get("chunks", [])],
        "total_chunks": len(data.get("chunks", [])),
        "availablility": "in_stock",
        "image_url": data.get("image_url", ""),
        "product_url": data.get("product_url", ""),
        "_partitionKey": data.get("category", "unknown")
    }

def upload_file_to_cosmosdb(file_path:str):
    """Upload parsed JSON data to Azure CosmosDB."""
    print(f"Uploading data from {file_path} to CosmosDB...")

    if file_path is None or file_path.strip() == "":
        print("Invalid file path provided.")
        return
    if os.path.exists(file_path) == False:
        print(f"File not found: {file_path}")
        return

    # Initialize the Cosmos client
    client = CosmosClient(COSMOSDB_ENDPOINT, DefaultAzureCredential())

    # Get a database
    database_name = COSMOSDB_NAME
    database = client.get_database_client(database_name)

    # Create (or get) a container
    container_name = COSMOSDB_CONTAINER
    container = database.get_container_client(container_name)

    # Load data from JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Uploading {len(data)} documents to CosmosDB container '{container_name}' in database '{database_name}'.")
    random_indexes = random.sample(range(11, len(data)), min(10, len(data)))
    print("Sample documents to be uploaded:", len(random_indexes))
    for idx in random_indexes:
        doc = data[idx]
        try:
            container.create_item(body=transform_document_body(doc))
            print(f"Uploaded document ID: {doc.get('id')}, Category: {doc.get('category')}, Name: {doc.get('name')[0:20]}...")
        except Exception as e:
            print(f"Error uploading document ID: {doc.get('id')}, Error: {str(e)}")
            traceback.print_exc()

    # Upload each document to the container
    # for doc in data[0:10]:# Limit to 2 item for testing
    
    print("Upload complete.")
    

if __name__ == "__main__":
    file_path = "c:/personal/_ProductSupportAIAgent/datasets/product_data/amazon_50.json"
    upload_file_to_cosmosdb(file_path)

    print("Done.")