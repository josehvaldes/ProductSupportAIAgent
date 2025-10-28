from sentence_transformers import SentenceTransformer
from shopassist_api.application.interfaces.service_interfaces import EmbeddingServiceInterface
from shopassist_api.application.settings.config import settings

class TransformersEmbeddingService(EmbeddingServiceInterface):
    """Service for generating embeddings using Transformers models."""
    def __init__(self, model_name: str):
        self.model = None
        self.model_name = model_name
        self._initialize_client()
        self.DIMENSION = 768  # Example dimension for 'sentence-transformers/multi-qa-mpnet-base-dot-v1'

    def _initialize_client(self):
        """Initialize the Transformers model based on configuration."""
        if not self.model_name:
            self.model_name = settings.embedding_model or "sentence-transformers/multi-qa-mpnet-base-dot-v1"
        self.model = SentenceTransformer(self.model_name)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(text.split())  # Simple token count based on whitespace

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for single text using Transformers model."""
        embedding = self.model.encode(text)
        return embedding.tolist()

    def generate_embedding_batch(self, input_texts: list[str], batch_size: int = 50) -> list[dict]:
        """Generate embeddings for a list of input texts."""
        all_embeddings = []
        for i in range(0, len(input_texts), batch_size):
            batch = input_texts[i:i + batch_size]
            embeddings = self.model.encode(batch)
            for j in range(len(batch)):
                all_embeddings.append({
                    "id": i + j,
                    "embedding": embeddings[j].tolist(),
                    "text": batch[j]
                })
        return all_embeddings
    