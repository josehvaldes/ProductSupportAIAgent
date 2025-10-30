import asyncio
import traceback
import tiktoken
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from shopassist_api.application.settings.config import settings
from shopassist_api.application.interfaces.service_interfaces import EmbeddingServiceInterface
from shopassist_api.infrastructure.services.azure_credential_manager import get_credential_manager
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

class OpenAIEmbeddingService(EmbeddingServiceInterface):
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model or "text-embedding-3-small"
        
        # Use shared credential manager
        credential_manager = get_credential_manager()
        token_provider = credential_manager.get_openai_token_provider()
        
        self.client = AzureOpenAI(
            api_version=settings.azure_openai_api_version or "2024-02-01",
            azure_endpoint=settings.azure_openai_endpoint,
            azure_ad_token_provider=token_provider
        )
        self.DIMENSION = 1536

        self.encoding = tiktoken.encoding_for_model(self.model_name)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def generate_embedding(self, input_text: str) -> list[float]:
        """Generate embedding for the given input text."""
        try:
            print("Generating embedding for single text...")
            response = self.client.embeddings.create(
                input=[input_text],
                model=self.model_name
            )
            print("Response:")
            print(response.data[0])
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
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model_name
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