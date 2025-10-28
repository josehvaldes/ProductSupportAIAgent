import asyncio
import traceback
import tiktoken
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from shopassist_api.application.settings.config import settings
from shopassist_api.application.interfaces.service_interfaces import EmbeddingServiceInterface
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

class OpenAIEmbeddingService(EmbeddingServiceInterface):
    def __init__(self):
        self.api_base = None
        self.api_version = None
        self.default_embedding_model = None
        self.deployment_name = None
        self.client = None
        self.encoding = None
        self.DIMENSION = 1536  # Example dimension for 'text-embedding-3-small'
        self._initialize_client()    
    
    def _initialize_client(self):
        """Initialize the OpenAI client based on configuration."""

        self.api_base = settings.azure_openai_endpoint 
        self.api_version = settings.azure_openai_api_version or "2024-02-01"
        self.default_embedding_model = settings.azure_openai_embedding_model or "text-embedding-3-small" #"gpt-3.5-turbo" #
        self.deployment_name = settings.azure_openai_embedding_model_deployment # "text-embedding-3-small_POC"
        
        self.encoding = tiktoken.encoding_for_model("text-embedding-3-small")

        token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

        client = AzureOpenAI(
            api_version = self.api_version, 
            azure_endpoint = self.api_base,
            azure_ad_token_provider=token_provider
        )

        self.client = client

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
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
        
    def generate_embedding_batch(self, input_texts: list[str], batch_size: int = 100) -> list[dict]:
        """Generate embeddings for a list of input texts."""
        all_embeddings = []

        for i in range(0, len(input_texts), batch_size):
            batch = input_texts[i:i + batch_size]

            try:
                response = self.client.Embedding.create(
                    input=batch,
                    model=self.deployment_name
                )
                
                # Extract embeddings
                for j, item in enumerate(response.data):
                    all_embeddings.append({
                        "index": i + j,
                        "embedding": item.embedding,
                        "text": batch[j]
                    })
                
                logger.info(f"Batch {i//batch_size + 1}: {len(batch)} texts, ")

                # Rate limiting: sleep between batches
                if i + batch_size < len(input_texts):
                    asyncio.sleep(0.5)
                
                
            except Exception as e:
                logger.error(f"Error in batch {i//batch_size + 1}: {e}")
                traceback.print_exc()
                raise
        
        logger.info(
            f"Total: {len(all_embeddings)} embeddings, "
            f"{self.total_tokens} tokens, ${self.total_cost:.6f}"
        )
        
        return all_embeddings