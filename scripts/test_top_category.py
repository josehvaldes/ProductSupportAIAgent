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
from shopassist_api.infrastructure.services.cosmos_product_service import CosmosProductService

# Instantiate services
vector_service = MilvusService()
embedding_service = TransformersEmbeddingService(model_name=settings.transformers_embedding_model)
product_service = CosmosProductService()
# Create retrieval service with injected dependencies
retrieval_service = RetrievalService(
    vector_service=vector_service,
    embedding_service=embedding_service,
    repository_service=product_service
)

async def evaluate_retrieval():
    query = "printer canon inkjet"
    print(f"🧪 Evaluating Top Category Retrieval for query: '{query}'\n")
    top_categories = await retrieval_service.retrieve_top_categories(query, top_k=2)
    print(f"Top Categories Retrieved:")
    for cat in top_categories:
        print(f"  Category: {cat['name']}, Score: {cat['distance']} {cat['full_name']}")

    query = "smartphone with good camera"
    print(f"\n🧪 Evaluating Top Category Retrieval for query: '{query}")
    top_categories = await retrieval_service.retrieve_top_categories(query, top_k=2)
    print(f"Top Categories Retrieved:")
    for cat in top_categories:
        print(f"  Category: {cat['name']}, Score: {cat['distance']} {cat['full_name']}")


    query = "cellphones with good camera"
    print(f"\n🧪 Evaluating Top Category Retrieval for query: '{query}")
    top_categories = await retrieval_service.retrieve_top_categories(query, top_k=2)
    print(f"Top Categories Retrieved:")
    for cat in top_categories:
        print(f"  Category: {cat['name']}, Score: {cat['distance']} {cat['full_name']}")

if __name__ == "__main__":
    asyncio.run(evaluate_retrieval())