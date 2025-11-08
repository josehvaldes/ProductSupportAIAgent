import asyncio
import json
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)
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

async def test_llm_response():
    """
    🧪 Testing OpenAI LLM service...
    """
    logger.warning("🧪 Testing OpenAI LLM service...\n")

    llm_service = OpenAILLMService( model_name=settings.azure_openai_nano_model,
                                     deployment_name=settings.azure_openai_nano_model_deployment)
    llm_context_builder = LLMSufficiencyBuilder(
        llm_service=llm_service
    )

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


if __name__ == "__main__":
    asyncio.run(test_llm_response())