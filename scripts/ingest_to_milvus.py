import json
import jsonlines
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
from shopassist_api.infrastructure.services.milvus_service import MilvusService

sys.path.append('../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)
from shopassist_api.application.settings.config import settings

product_jsonl_file = "c:/personal/_ProductSupportAIAgent/datasets/product_data/amazon_100_with_transformers_embeddings.jsonl"
knowledge_base_jsonl_file = "c:/personal/_ProductSupportAIAgent/ProductSupportAIAgent/scripts/knowledge_base_chunked/kb_with_embeddings.jsonl "

def load_json(file_path: str):
    with open(file_path, 'r') as f:
        return json.load(f)
    
def load_jsonl(file_path: str):
    data = []
    with jsonlines.open(file_path, 'r') as reader:
        for obj in reader:
            data.append(obj)
    return data

def main( option: str):
    print("🚀 Starting Milvus ingestion...\n")
    
    # Initialize service
    milvus_service = MilvusService(
        host="localhost",  # Change to Azure DNS if deployed
        port="19530"
    )
    
    if option in ["products", "both"]:
        # 1. Ingest products
        print("📦 Ingesting product embeddings...")
        products = load_jsonl(product_jsonl_file)
        print(f"Loaded {len(products)} product chunks")
        
        # Batch insert (100 at a time)
        batch_size = 100
        total_inserted = 0
        
        for i in tqdm(range(0, len(products), batch_size)):
            batch = products[i:i+batch_size]
            count = milvus_service.insert_products(batch)
            total_inserted += count
        
        print(f"✅ Inserted {total_inserted} product chunks\n")

    if option in ["knowledgebase", "both"]:

        # 2. Ingest knowledge base
        print("📚 Ingesting knowledge base embeddings...")
        kb_chunks = load_jsonl(knowledge_base_jsonl_file)
        print(f"Loaded {len(kb_chunks)} KB chunks")
        
        count = milvus_service.insert_knowledge_base(kb_chunks)
        print(f"✅ Inserted {count} knowledge base chunks\n")
    
    # 3. Print statistics
    print("📊 Collection Statistics:")
    
    products_stats = milvus_service.get_collection_stats("products_collection")
    print(f"   Products: {products_stats['num_entities']} vectors")
    
    kb_stats = milvus_service.get_collection_stats("knowledge_base_collection")
    print(f"   Knowledge Base: {kb_stats['num_entities']} vectors")
    
    print("\n✅ Ingestion complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embedding Generation Script")
    parser.add_argument("option", type=str, help="Products, KnowledgeBase, or Both")
    args = parser.parse_args()
    main(args.option.lower())