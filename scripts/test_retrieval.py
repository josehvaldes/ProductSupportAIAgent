import asyncio
import sys
import json
from tqdm import tqdm
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)

from shopassist_api.application.settings.config import settings

from shopassist_api.application.services.retrieval_service import RetrievalService
from shopassist_api.infrastructure.services.milvus_service import MilvusService
from shopassist_api.infrastructure.services.transformers_embedding_service import TransformersEmbeddingService
from shopassist_api.application.services.query_processor import QueryProcessor
from shopassist_api.infrastructure.services.cosmos_product_service import CosmosProductService

# Test queries with expected results
TEST_QUERIES = [
    # {
    #     "query": "laptop for video editing",
    #     "type": "product_search",
    #     "expected_category": "Laptops",
    #     "expected_keywords": ["video", "editing", "performance"]
    # },
    # {
    #     "query": "wireless headphones under $100",
    #     "type": "product_search",
    #     "expected_category": "Headphones",
    #     "max_price": 100
    # },
    # {
    #     "query": "what is your return policy",
    #     "type": "policy",
    #     "expected_doc_type": "policies"
    # },
    {
        "query": "MacBook Air M2",
        "type": "product_search",
        "expected_category": "Laptops",
    }
    # Add more test queries...
]

# Instantiate services
vector_service = MilvusService()
embedding_service = TransformersEmbeddingService(model_name=settings.transformers_embedding_model)
category_embedder_service = TransformersEmbeddingService(model_name=settings.transformers_category_embedding_model)
product_service = CosmosProductService()

# Create retrieval service with injected dependencies
retrieval_service = RetrievalService(
    vector_service = vector_service,
    embedding_service=embedding_service,
    category_embedder_service=category_embedder_service,
    repository_service=product_service
    
)


async def evaluate_retrieval_adaptative():
    """
    Evaluate retrieval quality with adaptative radius
    """
    queries = [
        # {
        #     "query": "MacBook Air M2",
        # },
        # {
        #     "query": "Samsung Galaxy S21",
        # },
        # {
        #     "query": "bluetooth headphones",
        # },
        {
            "query": "boAt BassHeads",
        },
    ]
    for test in queries:
        query = test['query']
        print(f"\n📝 Testing: '{query}'")
        
        retrieved = await retrieval_service.retrieve_products_adaptative(query, top_k=1, 
                                                                  enriched=True)

        print(f"   Retrieved {len(retrieved)} results")
        for res in retrieved:
            print(f"   Retrieved: {res}")        


async def evaluate_retrieval():
    """
    Evaluate retrieval quality
    """
    print("🧪 Evaluating Retrieval Quality\n")
    
    processor = QueryProcessor()
    
    results = {
        "total_queries": len(TEST_QUERIES),
        "successful": 0,
        "failed": 0,
        "details": []
    }
    
    for test in TEST_QUERIES:
        query = test['query']
        print(f"\n📝 Testing: '{query}'")
        
        # Classify
        query_type = test["type"]
        cleaned_query, extracted_filters = processor.process_query(query)
        print(f"   🔍 Classified as: {query_type}")
        print(f"   🧹 Cleaned query: {cleaned_query}")
        print(f"   🛠️  Extracted filters: {extracted_filters}")

        # Retrieve
        if query_type == 'product_search':
            retrieved = await retrieval_service.retrieve_products(cleaned_query, top_k=5, 
                                                                  filters=extracted_filters, 
                                                                  enriched=False)
        else:
            retrieved = await retrieval_service.retrieve_knowledge_base(query, top_k=3)
        
        # Evaluate
        success = len(retrieved) > 0
        print(f"   Retrieved {len(retrieved)} results")
        print(f"   Top result: {retrieved[0] if retrieved else 'N/A'}") 
        if success:
            results["successful"] += 1
            print(f"   ✅ Retrieved {len(retrieved)} results")
            
            # Check relevance
            if 'expected_category' in test:
                top_category = retrieved[0].get('category', '')
                if test['expected_category'] in top_category:
                    print(f"   ✅ Category match: {top_category}")
                else:
                    print(f"   ⚠️  Category mismatch: expected {test['expected_category']}, got {top_category}")
            else:
                print("   ℹ️  No expected category to verify")
        else:
            results["failed"] += 1
            print("   ❌ No results retrieved")
        
        results["details"].append({
            "query": query,
            "success": success,
            "num_results": len(retrieved),
            "top_score": retrieved[0].get('relevance_score', 0) if retrieved else 0
        })
    
    # Summary
    print("\n" + "="*50)
    print("📊 Evaluation Summary")
    print("="*50)
    print(f"Total queries: {results['total_queries']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"Success rate: {results['successful']/results['total_queries']*100:.1f}%")
    
    # Save results
    with open('retrieval_evaluation.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Results saved to retrieval_evaluation.json")

if __name__ == "__main__":
    asyncio.run(evaluate_retrieval_adaptative())