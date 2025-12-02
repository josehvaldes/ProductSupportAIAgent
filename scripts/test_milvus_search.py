import asyncio
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)
from shopassist_api.application.settings.config import settings
from shopassist_api.infrastructure.services.milvus_service import MilvusService
from shopassist_api.infrastructure.services.transformers_embedding_service import TransformersEmbeddingService

async def test_search():
    print("🧪 Testing Milvus vector search...\n")
    
    # Initialize services
    milvus = MilvusService()
    embedder = TransformersEmbeddingService(settings.transformers_embedding_model)
    
    # Test queries
    test_queries = [
        "laptop for video editing",
        "wireless headphones under $100",
        "what is the return policy",
        "shipping information"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        
        # Generate query embedding
        query_embedding = await embedder.generate_embedding(query)
        
        # Determine collection
        is_policy_query = any(word in query.lower() for word in ['policy', 'return', 'shipping', 'warranty'])
        
        # Search
        start_time = time.time()
        
        if is_policy_query:
            results = milvus.search_knowledge_base(query_embedding, top_k=3)
        else:
            results = milvus.search_products(query_embedding, top_k=5)
        
        latency = (time.time() - start_time) * 1000  # ms
        
        # Display results
        print(f"   Latency: {latency:.2f}ms")
        print(f"   Results: {len(results)}")
        
        for i, result in enumerate(results[:3], 1):
            print(f"\n   {i}. Score: {result['distance']:.4f}")
            print(f"      Text: {result['text'][:100]}...")
            if 'product_id' in result:
                print(f"      Product: {result['product_id']} | {result['brand']} | ${result['price']}")
            elif 'doc_type' in result:
                print(f"\n      Doc Type: {result['doc_type']}")
    
    print("\n✅ Search tests complete!")

if __name__ == "__main__":
    asyncio.run(test_search())