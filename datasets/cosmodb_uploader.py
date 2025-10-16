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
        "title": data.get("title", ""),
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
    # Upload each document to the container
    for doc in data: #data[0:1]:# Limit to first item for testing
        try:
            container.create_item(body=transform_document_body(doc))
            print(f"Uploaded document ID: {doc.get('id')}, Category: {doc.get('category')}, Title: {doc.get('title')[0:20]}...")
        except Exception as e:
            print(f"Error uploading document ID: {doc.get('id')}, Error: {str(e)}")
            traceback.print_exc()
    
    print("Upload complete.")
    

if __name__ == "__main__":
    file_path = "amazon_50.json"
    upload_file_to_cosmosdb(file_path)

    # with open(file_path, 'r', encoding='utf-8') as f:
    #     data = json.load(f)
    #     body = get_document_body(data[0])
    #     print(json.dumps(body, indent=4))

    print("Done.")