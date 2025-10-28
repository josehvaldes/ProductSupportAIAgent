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

def main():
   # Connect to Milvus
    connections.connect(
        alias="default",
        host="localhost",  # or your Azure DNS
        port="19530"
    )
    
    print("🔗 Connected to Milvus")
    
    # Drop existing collections if they exist
    if utility.has_collection("products_collection"):
        utility.drop_collection("products_collection")
        print("Dropped existing products_collection")
    
    if utility.has_collection("knowledge_base_collection"):
        utility.drop_collection("knowledge_base_collection")
        print("Dropped existing knowledge_base_collection")
    
    # Create collections
    create_products_collection()
    create_knowledge_base_collection()
    
    # List collections
    collections = utility.list_collections()
    print(f"\n📚 Available collections: {collections}")


if __name__ == "__main__":
    main()