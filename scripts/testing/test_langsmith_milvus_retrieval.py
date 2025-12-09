import os
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_milvus import Milvus 
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser  
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_huggingface import HuggingFaceEmbeddings

from langsmith import traceable, uuid7
id = uuid7()

import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('../../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent.parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)
from shopassist_api.application.settings.config import settings



# Helper function to format docs
def format_docs(docs): #:Document[]
    return "\n\n".join(doc.page_content for doc in docs)

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
# embeddings = AzureOpenAIEmbeddings(
#     azure_endpoint=settings.azure_openai_endpoint,
#     api_version=settings.azure_openai_api_version,
#     azure_ad_token_provider=token_provider,
#     azure_deployment=settings.azure_openai_embedding_model_deployment   
# )

cat_embeddings = HuggingFaceEmbeddings(model_name=settings.transformers_category_embedding_model)
# Connect to your existing Milvus
cat_vectorstore = Milvus(
    embedding_function=cat_embeddings,
    collection_name="categories_collection",
    connection_args={"host": "localhost", "port": "19530"},
    vector_field="full_embedding",
    text_field="full_name"
)


embeddings = HuggingFaceEmbeddings(model_name=settings.transformers_embedding_model)

# Connect to your existing Milvus
vectorstore = Milvus(
    embedding_function=embeddings,
    connection_args={"host": "localhost", "port": "19530"},
    collection_name="products_collection",
    vector_field="embedding",
    text_field="text"
)


# Create retrieval chain
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

#test retrieval
docs = retriever.invoke("looking for wireless headphones")
print("Retrieved Documents:")
for index, doc in enumerate(docs):
    print(f"Document {index + 1}: {doc.page_content[0:200]}...")  # Print first 200 characters  

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are ShopAssist, an intelligent product support assistant for an electronics store. Use the given products in the context to answer the question. \nContext: {context}"),
    ("human", "{question}"),
])


rag_chain = (
    RunnableParallel(
        context=retriever| format_docs,
        question=RunnablePassthrough()
    )
    | prompt
    | llm
    | StrOutputParser()
)

response = rag_chain.invoke("I need headphones for samsumg z flip?")
print("Response from RAG chain:")
print(response)