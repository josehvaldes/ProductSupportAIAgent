import json
import traceback
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from collections import defaultdict

class openaiService:
    def __init__(self, settings):
        self.api_base = settings.azure_openai_endpoint 
        self.api_version = settings.azure_openai_api_version or "2024-02-01"
        self.default_embedding_model = settings.azure_openai_default_model or "text-embedding-3-small" #"gpt-3.5-turbo" #
        self.deployment_name = settings.azure_openai_model_deployment # "text-embedding-3-small_POC"

        self._initialize_client()    
    
    def _initialize_client(self):
        """Initialize the OpenAI client based on configuration."""
        
        token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

        client = AzureOpenAI(
            api_version = self.api_version, 
            azure_endpoint = self.api_base,
            azure_ad_token_provider=token_provider
        )

        self.client = client

    def generate_embedding(self, input_text: str) -> list[float]:
        """Generate embedding for the given input text."""
        try:
            response = self.client.Embedding.create(
                input=[input_text],
                model=self.deployment_name
            )
            embedding = response.data[0].embedding
            return embedding
        except Exception as e:
            print("An error occurred while generating embedding:")
            traceback.print_exc()
            return []