import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

sys.path.append('../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)
from shopassist_api.application.services.formaters import FormatterUtils
from shopassist_api.application.services.rag_service import RAGService
from shopassist_api.infrastructure.services.cosmos_product_service import CosmosProductService
from shopassist_api.infrastructure.services.openai_llm_service import OpenAILLMService
from shopassist_api.application.settings.config import settings
from shopassist_api.application.services.llm_sufficiency_builder import LLMSufficiencyBuilder

from shopassist_api.logging_config import setup_logging
from shopassist_api.logging_config import get_logger

setup_logging(
        log_level=settings.log_level,
        log_file=settings.log_file,
        log_to_console=settings.log_to_console
    )
logger = get_logger(__name__)

# llm_service = OpenAILLMService( model_name=settings.azure_openai_nano_model,
#                                       deployment_name=settings.azure_openai_nano_model_deployment)

llm_service = OpenAILLMService( model_name=settings.azure_openai_model,
                                     deployment_name=settings.azure_openai_model_deployment)

llm_context_builder = LLMSufficiencyBuilder(
    llm_service=llm_service
)

async def test_llm_response():
    """
    🧪 Testing OpenAI LLM service...
    """
    logger.warning("🧪 Testing OpenAI LLM service...\n")

    test_prompts = [
        {
            "prompt": "Find me a smartphone with a good camera and long battery life.",
            "history": "",
            "expected_result": {
                "is_sufficient": "no",
                "intent_query": "product_search",
                "scope_retrieval_hint": None,
                "query_retrieval_hint": None
            }
        },
        {
            "prompt": "What is the return policy for electronics?",
            "expected_result": {
                "is_sufficient": "no",
                "intent_query": "policy_question",
                "scope_retrieval_hint": None,
                "query_retrieval_hint": None
            }
        }
    ]

    for idx, item in enumerate(test_prompts):
        prompt = item['prompt']
        
        context = await llm_context_builder.analyze_sufficiency(
            query=prompt,
            history=""
        )
        print(f"\n📝 Test[{idx}] Prompt: '{prompt}'")
        print(f"🧩 [{idx}] Built Context: {json.dumps(context, indent=4)}", flush=True)



async def test_llm_response_with_history():
    
    repository = CosmosProductService()
    
    history = await repository.get_conversation_history("5061c45b-01d8-4725-92f5-a679bbeb2add")
    history_text = FormatterUtils.format_history(history)
    
    print(f"\n🧩 Formatted History: {history_text}")

    history_prompts = [
        {
            "prompt": "which one has Wi-Fi connector?",
            "history": history_text,
            "expected_result": {
                "is_sufficient": "Yes", # Based on history about laptops
                "intent_query": "product_comparison",
                "scope_retrieval_hint": None,
                "query_retrieval_hint": None
            }
        }
    ]

    for idx, item in enumerate(history_prompts):
        prompt = item['prompt']
        
        context = await llm_context_builder.analyze_sufficiency(
            query=prompt,
            history=item['history']
        )
        print(f"\n📝 Test[{idx}] Prompt: '{prompt}'")
        print(f"🧩 [{idx}] Built Context: {json.dumps(context, indent=4)}")
        expected = item.get('expected_result', {})
        print(f" Expected sufficient: {expected.get('is_sufficient', '')} | Got: {context.get('is_sufficient', '')}")

if __name__ == "__main__":
    #asyncio.run(test_llm_response())
    asyncio.run(test_llm_response_with_history())