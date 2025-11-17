import argparse

from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)

def create_products_collection():
    """Create products collection with vector index"""
    # Define fields
    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
        FieldSchema(name="product_id", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=5000),
        # Adjust dimension as needed. Use 1536 for OpenAI 'text-embedding-3-small' or 768 for MiniLM
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
        FieldSchema(name="chunk_index", dtype=DataType.INT64),
        FieldSchema(name="total_chunks", dtype=DataType.INT64),
        FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="price", dtype=DataType.FLOAT),
        FieldSchema(name="brand", dtype=DataType.VARCHAR, max_length=100)
    ]
    
    # Create schema
    schema = CollectionSchema(
        fields=fields,
        description="Product chunks with embeddings"
    )
    
    # Create collection
    collection = Collection(
        name="products_collection",
        schema=schema
    )
    
    # Create HNSW index for vector field
    index_params = {
        "metric_type": "COSINE",  # or "L2", "IP"
        "index_type": "HNSW",
        "params": {
            "M": 16,  # Max connections per layer
            "efConstruction": 256  # Search depth during construction
        }
    }
    
    collection.create_index(
        field_name="embedding",
        index_params=index_params
    )
    
    print(f"✅ Created collection: products_collection")
    return collection

def create_knowledge_base_collection():
    """Create knowledge base collection"""
    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
        FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=5000),
        FieldSchema(name="chunk_index", dtype=DataType.INT64),
        # Adjust dimension as needed. Use 1536 for OpenAI 'text-embedding-3-small' or 768 for MiniLM
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768), 
        FieldSchema(name="doc_type", dtype=DataType.VARCHAR, max_length=50)
    ]
    
    schema = CollectionSchema(
        fields=fields,
        description="Knowledge base chunks with embeddings"
    )
    
    collection = Collection(
        name="knowledge_base_collection",
        schema=schema
    )
    
    # Create index
    index_params = {
        "metric_type": "COSINE",
        "index_type": "HNSW",
        "params": {"M": 16, "efConstruction": 256}
    }
    
    collection.create_index(
        field_name="embedding",
        index_params=index_params
    )
    
    print(f"✅ Created collection: knowledge_base_collection")
    return collection

def create_categories_collection():
    """Create categories collection"""
    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
        FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="full_name", dtype=DataType.VARCHAR, max_length=1000),
        # Adjust dimension as needed. Use 1024 for intfloat/e5-large-v2
        # Use 768 for sentence-transformers/multi-qa-mpnet-base-dot-v1
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024), # Adjust dimension as needed
        FieldSchema(name="full_embedding", dtype=DataType.FLOAT_VECTOR, dim=1024), # Adjust dimension as needed

    ]
    
    schema = CollectionSchema(
        fields=fields,
        description="Product categories"
    )
    
    collection = Collection(
        name="categories_collection",
        schema=schema
    )

        # Create index
    index_params = {
        "metric_type": "COSINE",
        "index_type": "HNSW",
        "params": {"M": 16, "efConstruction": 256}
    }
    
    collection.create_index(
        field_name="embedding",
        index_params=index_params
    )
    
    collection.create_index(
        field_name="full_embedding",
        index_params=index_params
    )

    print(f"✅ Created collection: categories_collection")
    return collection

def main():

    parser = argparse.ArgumentParser(description="Embedding Generation Script")
    parser.add_argument("option", type=str, help="Products, KnowledgeBase, Categories, or All")
    args = parser.parse_args()
    option = args.option.lower()
    

   # Connect to Milvus
    connections.connect(
        alias="default",
        host="localhost",  # or your Azure DNS
        port="19530"
    )
    
    print("🔗 Connected to Milvus")
    
    if option in ["products", "all"]:
        # Drop existing collections if they exist
        if utility.has_collection("products_collection"):
            utility.drop_collection("products_collection")
            print("Dropped existing products_collection")
        create_products_collection()
    
    if option in ["knowledgebase", "all"]:
        if utility.has_collection("knowledge_base_collection"):
            utility.drop_collection("knowledge_base_collection")
            print("Dropped existing knowledge_base_collection")
        create_knowledge_base_collection()

    if option in ["categories", "all"]:
        if utility.has_collection("categories_collection"):
            utility.drop_collection("categories_collection")
            print("Dropped existing categories_collection")

        create_categories_collection()
    
    # List collections
    collections = utility.list_collections()
    print(f"\n📚 Available collections: {collections}")


if __name__ == "__main__":
    main()