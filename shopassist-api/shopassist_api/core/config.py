"""
Core configuration settings for the Shop Assistant API.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    api_title: str = "Shop Assistant API"
    api_version: str = "0.1.0"
    debug: bool = False
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    
    # Azure Configuration
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: str = "2024-02-15-preview"

    azure_openai_default_model: Optional[str] = None
    azure_openai_model_deployment: Optional[str] = None
    


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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
