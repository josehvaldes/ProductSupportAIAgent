import os
import json
import random
import re
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
import traceback

COSMOSDB_ENDPOINT = "https://cdb-shopassist-ai-test-01.documents.azure.com:443/"
COSMOSDB_NAME = "shopassist-ai"
COSMOSDB_PRODUCT_CONTAINER = "products"

def transform_document_body(data:dict) -> dict:
    """Generate a sample document body."""
    return {
        "id": data.get("id", ""),
        "name": data.get("name", ""),
        "description": data.get("description", ""),
        "category": data.get("category", ""),
        "category_full": ' > '.join(data.get("category_full", [])),
        "price": data.get("price", 0.0),
        "brand": data.get("brand", ""),
        "rating": data.get("rating", 0.0),
        "review_count": data.get("review_count", 0.0),
        "chunks": [ chunk for chunk in data.get("chunks", [])],
        "total_chunks": len(data.get("chunks", [])),
        "availability": "in_stock",
        "image_url": data.get("image_url", ""),
        "product_url": data.get("product_url", ""),
        "_partitionKey": data.get("category", "unknown")
    }

def transform_category_body(data:dict) -> dict:
    """Generate a sample category document body."""
    parts = data.get("category_full", [])
    normalized_parts = []
    for part in parts:
        # Remove special chars, lowercase, remove spaces
        clean = re.sub(r'[^a-zA-Z0-9]+', '', part).lower()
        normalized_parts.append(clean)

    category_id =  '.'.join(normalized_parts)
    category_name = data.get("category")
    category_full = ' > '.join(data.get("category_full", []))
    
    category_item = {
        "id": category_id,
        "name": category_name,
        "full_name": category_full,
    }

    return category_item

def upload_file_to_cosmosdb(file_path:str, output_categories_file:str=None):
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
    container_name = COSMOSDB_PRODUCT_CONTAINER
    container = database.get_container_client(container_name)

    # Load data from JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Uploading {len(data)} documents to CosmosDB container '{container_name}' in database '{database_name}'.")
    random_indexes = random.sample(range(len(data)), min(10, len(data))) 
    print("Sample documents to be uploaded:", len(random_indexes))
    #for idx in random_indexes:
    #doc = data[idx]
    categories = {}
    for doc in data:
        try:
   
            #container.create_item(body=transform_document_body(doc))
            print(f"Uploaded document ID: {doc.get('id')}, Category: {doc.get('category')}, Name: {doc.get('name')[0:20]}...")
            
            category_doc = transform_category_body(doc)
            if category_doc["id"] not in categories:
                categories[category_doc["id"]] = category_doc
                    
        except Exception as e:
            print(f"Error uploading document ID: {doc.get('id')}, Error: {str(e)}")
            traceback.print_exc()

    print(f"Uploading {len(categories)} distinct categories to CosmosDB category container.")
    try:
        with open(output_categories_file, 'w', encoding='utf-8') as f:
            json.dump(list(categories.values()), f, indent=4)
            
        print(f"Saved categories to {output_categories_file}")
    except Exception as e:
        print("Error saving to JSON:", e)
        traceback.print_exc()


    print("Upload complete.")
    


if __name__ == "__main__":
    file_path = "c:/personal/_ProductSupportAIAgent/datasets/product_data/amazon_50.json"
    output_categories_file = "c:/personal/_ProductSupportAIAgent/datasets/product_data/amazon_50_categories.json"
    upload_file_to_cosmosdb(file_path, output_categories_file)

    print("Done.")