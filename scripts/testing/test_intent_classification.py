import asyncio
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('../../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent.parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)
from shopassist_api.infrastructure.services.openai_llm_service import OpenAILLMService
from shopassist_api.application.services.intent_classifier import IntentClassifier
from shopassist_api.application.settings.config import settings

async def test_llm_response():
    print("🧪 Testing OpenAI LLM service...\n")
    
    #test intent classifier with nano model
    llm_service = OpenAILLMService( model_name=settings.azure_openai_nano_model,
                                     deployment_name=settings.azure_openai_nano_model_deployment)
    
    classifier = IntentClassifier(llm_service)
    test_prompts = [
        {
            "prompt": "Find me a smartphone with a good camera and long battery life.",
            "expected_intent": "product_search"
        },
        {
            "prompt": "What is the return policy for electronics?",
            "expected_intent": "policy_question"
        }
        ,
        {
            "prompt": "Can you compare the latest laptops for gaming?",
            "expected_intent": "product_comparison"
        },
        {
            "prompt": "Tell me a joke about computers.",
            "expected_intent": "chitchat"
        },
        {
            "prompt": "How do I reset my account password?",
            "expected_intent": "general_support"
        },
        {
            "prompt": "What are your store hours?",
            "expected_intent": "policy_question"
        },
        {
            "prompt": "give me details of the samsung z flip 5?",
            "expected_intent": "product_details"
        },
    ]
    
    for item in test_prompts:
        prompt = item['prompt']
        expected_intent = item['expected_intent']
        print(f"\n📝 Prompt: '{prompt}'")
        
        start_time = time.time()
        response = await classifier.classify(
            user_message=prompt
        )
        latency = (time.time() - start_time) * 1000  # ms
        
        print(f"   Latency: {latency:.2f}ms")
        print(f"   Intent: {response[0]}, expected: {expected_intent}, match: {response[0] == expected_intent}")
        print(f"   Confidence: {response[1]}")

if __name__ == "__main__":
    asyncio.run(test_llm_response())

