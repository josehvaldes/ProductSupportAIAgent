import asyncio
import sys
import argparse
import time
import json
from tqdm import tqdm
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Optional, Tuple

sys.path.append('../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)

from shopassist_api.application.settings.config import settings
from shopassist_api.infrastructure.services.openai_llm_service import OpenAILLMService
from shopassist_api.infrastructure.services.milvus_service import MilvusService
from shopassist_api.infrastructure.services.transformers_embedding_service import TransformersEmbeddingService
from shopassist_api.infrastructure.services.cosmos_product_service import CosmosProductService
from shopassist_api.application.services.rag_service import RAGService
from shopassist_api.application.services.retrieval_service import RetrievalService

TEST_QUERIES = [
    # {
    #     "query": "I need a laptop for video editing under $1500",
    #     "expected_aspects": ["recommendations", "price", "specs", "video editing"]
    # },
    {
        "query": "What's your return policy?",
        "expected_aspects": ["return window", "conditions", "refund process"]
    },
    # {
    #     "query": "Do you have wireless headphones?",
    #     "expected_aspects": ["product list", "features", "prices"]
    # },
    # Add more...
]

async def evaluate_basic_prompt():
    """
      Evaluate basic prompt response"""
    print("🧪 Evaluating Basic Prompt\n")    
    llm = OpenAILLMService()
    print(f"Using LLM Service ready")
    vector_service = MilvusService()
    embedding_service = TransformersEmbeddingService(model_name=settings.transformers_embedding_model)
    product_service = CosmosProductService()
    
    print(f"Using Product Service ready")
    # Create retrieval service with injected dependencies
    retrieval_service = RetrievalService(
        vector_service=vector_service,
        embedding_service=embedding_service,
        repository_service=product_service
    )
    print(f"Using Retrieval Service ready")
    rag = RAGService(llm_service=llm, retrieval_service=retrieval_service)
    print(f"\n📝 Query: rivers and mountains")
    result = await rag.generate_test_answer(
        query="rivers and mountains"
    )
    
    response = result['response']
    print(f"\n💬 Response:\n{response}\n")
    print("End of basic prompt evaluation.")

async def evaluate_prompts():
    """
    Evaluate prompt quality and response relevance
    """
    print("🧪 Evaluating Prompt Performance\n")

    llm = OpenAILLMService()

    vector_service = MilvusService()
    embedding_service = TransformersEmbeddingService(model_name=settings.transformers_embedding_model)
    product_service = CosmosProductService()

    # Create retrieval service with injected dependencies
    retrieval_service = RetrievalService(
        vector_service=vector_service,
        embedding_service=embedding_service,
        repository_service=product_service
    )

    rag = RAGService(llm_service=llm, retrieval_service=retrieval_service)
    results = []
    
    for test in TEST_QUERIES:
        query = test['query']
        print(f"\n📝 Query: {query}")
        
        # Generate response
        result = await rag.generate_answer(query)
        
        response = result['response']
        print(f"\n💬 Response:\n{response}\n")
        print(f"📊 Tokens: {result['metadata']['tokens']['total']}")
        print(f"💰 Cost: ${result['metadata']['cost']:.6f}")
        print(f"📚 Sources: {result['metadata']['num_sources']}")
        
        # Manual evaluation placeholder
        print("\nManual Review:")
        print(f"Expected aspects: {test['expected_aspects']}")
        print("Rate this response (1-5):")
        
        results.append({
            "query": query,
            "response": response,
            "metadata": result['metadata']
        })
    
    # Save results
    with open('prompt_evaluation.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Evaluation complete! Results saved to prompt_evaluation.json")

if __name__ == "__main__":
    asyncio.run(evaluate_prompts())
    #asyncio.run(evaluate_basic_prompt())
    print("All evaluations completed.")