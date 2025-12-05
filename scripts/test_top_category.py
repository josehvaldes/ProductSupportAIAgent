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

from shopassist_api.logging_config import setup_logging
from shopassist_api.logging_config import get_logger

setup_logging(
        log_level=settings.log_level,
        log_file=settings.log_file,
        log_to_console=settings.log_to_console
    )
logger = get_logger(__name__)


# Instantiate services
vector_service = MilvusService()
embedder_service = TransformersEmbeddingService(model_name=settings.transformers_embedding_model)

category_embedder_service = TransformersEmbeddingService(model_name=settings.transformers_category_embedding_model)

product_service = CosmosProductService()
# Create retrieval service with injected dependencies
retrieval_service = RetrievalService(
    vector_service=vector_service,
    embedding_service=embedder_service,
    repository_service=product_service,
    category_embedder_service=category_embedder_service
)

async def evaluate_retrieval():

    queries = [
        # "printer canon inkjet",
        # "smartphone with good camera",
        # "cellphones with good camera",
        # "I need an smarttv with at least 32 inches screen",
        # "I need an smart tv with at least 32 inches screen",
        # "I need an smart television with at least 32 inches screen",
        # "Find me a smartphone with a good camera and long battery life."
        "case for Samsung z flip"
    ]

    for query in queries:
        print(f"\n🧪 Evaluating Top Category Retrieval for query: '{query}'")
        top_categories = await retrieval_service.retrieve_top_categories(query, top_k=3)
        print(f"Top Categories Retrieved: [{len(top_categories)}]")
        for cat in top_categories:
            print(f"  Score: {cat['score']}, Category: {cat['name']} , full_name: {cat['full_name']}")


async def evaluate_ambiguous_queries():

    queries = [
        "I need a cellphones with good camera",
        "I need to edit videos with a smartphone, which options do I have?",
        "looking for a selfie stick for my iPhone",
        "looking for a selfie stick and a backup battery pack for my iPhone",
    ]

    for query in queries:
        print(f"\n🧪 Evaluating Top Category Retrieval for query: '{query}")
        top_categories = await retrieval_service.retrieve_top_categories(query, top_k=3)
        print(f"Top Categories Retrieved: [{len(top_categories)}]")
        for cat in top_categories:
            print(f"  Score: {cat['score']}, Category: {cat['name']} , full_name: {cat['full_name']}")

async def one_word_query_test():

    queries = [
        "headphones",
        "smartphone",
        "printer",
        "television",
        "laptop",
        "camera",
        "tablet",
        "lightstick",
        "monitor",
        "router",
        "selfie stick"
    ]

    for query in queries:
        print(f"\n🧪 Evaluating Top Category Retrieval for query:: '{query}'")
        top_categories = await retrieval_service.retrieve_top_categories(query, top_k=3)
        print(f"Top Categories Retrieved: [{len(top_categories)}]")
        for cat in top_categories:
            print(f"  Score: {cat['score']}, Category: {cat['name']} , full_name: {cat['full_name']}")


if __name__ == "__main__":
    #asyncio.run(evaluate_ambiguous_queries())
    #asyncio.run(one_word_query_test())
    asyncio.run(evaluate_retrieval())