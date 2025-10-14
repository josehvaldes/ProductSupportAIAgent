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
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: str = "2024-02-15-preview"
    
    # Azure AI Search
    azure_search_endpoint: Optional[str] = None
    azure_search_key: Optional[str] = None
    azure_search_index: str = "products"
    
    # Azure Storage
    azure_storage_connection_string: Optional[str] = None
    azure_storage_container: str = "product-data"
    
    # Database Configuration
    database_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
