import os
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser  
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from langsmith import traceable, uuid7
id = uuid7()

import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)
from shopassist_api.application.settings.config import settings


@traceable(name="manual_embedding_trace")
def get_embedding(text: str):
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
        azure_ad_token_provider=token_provider,
        azure_deployment=settings.azure_openai_embedding_model_deployment   
    )
    return embeddings.embed_query(text)

# Azure OpenAI configuration (use your existing credentials)
print("Setting up Azure OpenAI client...")
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

print("Creating LangChain AzureChatOpenAI instance...")
llm = AzureChatOpenAI(
    azure_endpoint=settings.azure_openai_endpoint,
    api_version=settings.azure_openai_api_version,
    deployment_name=settings.azure_openai_model_deployment,
    azure_ad_token_provider=token_provider,
    temperature=0.3
)

print("Testing embedding generation...")
# Embedding model (for vector search)
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=settings.azure_openai_endpoint,
    api_version=settings.azure_openai_api_version,
    azure_ad_token_provider=token_provider,
    azure_deployment=settings.azure_openai_embedding_model_deployment   
)

# Simple chain for POC
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful product assistant."),
    ("user", "{query}")
])

chain = prompt | llm | StrOutputParser()

# Test queries
test_queries = [
    "Hello. What are you?",
]

print("Running LangSmith POC...")
print("Check traces at: https://smith.langchain.com/\n")

# for query in test_queries:
#     print(f"Query: {query}")
#     response = chain.invoke({"query": query})
#     print(f"Response: {response[:500]}...\n")
#     print("-" * 80)



print("2. Testing embed_query()...")
# query = "headphones for samsung z flip?"
# query_vector = embeddings.embed_query(query)  # For Milvus search

# print(f"Vector dimension: {len(query_vector)}")
# print(f"First 5 values: {query_vector[:5]}\n")

# # Test 3: Batch embeddings (check LangSmith for this)
# print("3. Testing embed_documents()...")
# texts = ["laptop", "headphones", "keyboard"]
# vectors = embeddings.embed_documents(texts)
# print(f"Generated {len(vectors)} vectors")
# print(f"Each vector has {len(vectors[0])} dimensions\n")

# # Test 4: Manual embedding trace
# print("4. Testing manual embedding trace...")
print("LANGCHAIN_TRACING_V2:", os.getenv("LANGCHAIN_TRACING_V2"))
print("LANGCHAIN_PROJECT:", os.getenv("LANGCHAIN_PROJECT"))
print("LANGCHAIN_API_KEY:", "set" if os.getenv("LANGSMITH_API_KEY") else "NOT SET")
vector = get_embedding("smartphone with good camera")
print(f"Manual embedding trace vector dimension: {len(vector)}")