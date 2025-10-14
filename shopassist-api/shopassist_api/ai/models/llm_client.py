"""
LLM Client for interfacing with language models (OpenAI, Azure OpenAI).
"""
import openai
from typing import Optional, Dict, Any
from shopassist_api.core.config import settings


class LLMClient:
    """
    Client for interacting with Large Language Models.
    """
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the OpenAI client based on configuration."""
        if settings.azure_openai_api_key and settings.azure_openai_endpoint:
            # Use Azure OpenAI
            self.client = openai.AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version
            )
            self.model = "gpt-4o"  # Default Azure model
        elif settings.openai_api_key:
            # Use OpenAI directly
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
        else:
            # No API key configured
            self.client = None
            self.model = None
    
    async def generate_response(
        self, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate a response using the configured LLM.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        if not self.client or not self.model:
            return "I'm sorry, the AI service is not properly configured. Please contact support."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"I'm sorry, I encountered an error: {str(e)}"
    
    async def generate_embedding(self, text: str) -> Optional[list]:
        """
        Generate embeddings for text (useful for semantic search).
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if error
        """
        if not self.client:
            return None
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception:
            return None
