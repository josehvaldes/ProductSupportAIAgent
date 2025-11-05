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
from shopassist_api.infrastructure.services.openai_llm_service import OpenAILLMService
from shopassist_api.application.services.intent_classifier import IntentClassifier
from shopassist_api.application.settings.config import settings

async def test_llm_response():
    print("🧪 Testing OpenAI LLM service...\n")
    
    llm_service = OpenAILLMService()
    classifier = IntentClassifier(llm_service)
    test_prompts = [
        "What is the return policy for electronics?",
        "Suggest a laptop for video editing under $1500.",
        "which is better for outdoor photography samsung s24 or iPhone 16 Pro Max"
        "Good morning chat, ready for looking sales today?"
    ]
    
    for prompt in test_prompts:
        print(f"\n📝 Prompt: '{prompt}'")
        
        start_time = time.time()
        response = await classifier.classify(
            user_message=prompt
        )
        latency = (time.time() - start_time) * 1000  # ms
        
        print(f"   Latency: {latency:.2f}ms")
        print(f"   Intent: {response[0]}")
        print(f"   Confidence: {response[1]}")

if __name__ == "__main__":
    asyncio.run(test_llm_response())

