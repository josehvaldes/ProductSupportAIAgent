"""
Core configuration settings for the Shop Assistant API.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    api_title: str = "Shop Assistant API"
    api_description: str = "AI-Powered Product Knowledge & Support Agent"
    api_version: str = "0.1.0"
    debug: bool = False

    use_dump_service: bool = True

    # Embedding Configuration
    embedding_provider: str = "azure_openai"  # Options: 'azure_openai', 'transformers'
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    
    # Azure Configuration
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: str = "2024-02-15-preview"

    azure_openai_embedding_model: Optional[str] = None
    azure_openai_embedding_model_deployment: Optional[str] = None
    
    #Transformers Configuration for EMBEDDING_PROVIDER = transformers
    transformers_embedding_model: Optional[str] = "sentence-transformers/multi-qa-mpnet-base-dot-v1"

    # Azure AI Search
    azure_search_endpoint: Optional[str] = None
    azure_search_key: Optional[str] = None
    azure_search_index: str = "products"
    
    # Azure Storage
    azure_storage_connection_string: Optional[str] = None
    azure_storage_container: str = "product-data"
    
    #Azure cosmosDB
    cosmosdb_endpoint: Optional[str] = None
    cosmosdb_database: str = "<shopassistdatabase>"
    cosmosdb_product_container: str = "products"
    cosmosdb_chat_container: str = "chats"


    # Database Configuration
    database_url: Optional[str] = None
    
    #Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/shopassist_api.log"
    log_to_console: bool = True

    # Milvus Configuration
    milvus_host: str = "localhost"
    milvus_port: str = "19530"
    milvus_product_collection: str = "products_collection"
    milvus_knowledge_base_collection: str = "knowledge_base_collection"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
