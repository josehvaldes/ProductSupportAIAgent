from sentence_transformers import SentenceTransformer
from shopassist_api.application.interfaces.service_interfaces import EmbeddingServiceInterface
from shopassist_api.application.settings.config import settings
from threading import RLock
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

# Module-level singleton with thread safety
_model_lock = RLock()
_model_cache = {}  # Cache multiple models by name

class TransformersEmbeddingService(EmbeddingServiceInterface):
    """Service for generating embeddings using Transformers models."""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.transformers_embedding_model or "sentence-transformers/multi-qa-mpnet-base-dot-v1"
        self._initialize_client()
        self.DIMENSION = 768  # Adjust based on model

    def _initialize_client(self):
        """Initialize the Transformers model based on configuration."""
        if settings.use_singleton_transformers_model:
            # Use cached model if available
            if self.model_name in _model_cache:
                logger.info(f"Using cached model: {self.model_name}")
                self.model = _model_cache[self.model_name]
            else:
                # Load model with thread safety
                with _model_lock:
                    # Double-check after acquiring lock
                    if self.model_name not in _model_cache:
                        logger.info(f"Loading model (first time): {self.model_name}")
                        _model_cache[self.model_name] = SentenceTransformer(self.model_name)
                    self.model = _model_cache[self.model_name]
        else:
            # Load new model instance each time (not recommended for production)
            logger.info(f"Loading new model instance: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        # Note: This is a rough approximation
        return len(text.split())

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for single text using Transformers model."""
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def generate_embedding_batch(self, input_texts: list[str], batch_size: int = 50) -> list[dict]:
        """Generate embeddings for a list of input texts."""
        all_embeddings = []
        for i in range(0, len(input_texts), batch_size):
            batch = input_texts[i:i + batch_size]
            embeddings = self.model.encode(batch, convert_to_tensor=False)
            for j in range(len(batch)):
                all_embeddings.append({
                    "id": i + j,
                    "embedding": embeddings[j].tolist(),
                    "text": batch[j]
                })
        return all_embeddings
    
    async def health_check(self) -> bool:
        """Ping the service to check connectivity"""
        try:
            # Simple check to see if model is loaded
            test_embedding = self.model.encode("test", convert_to_tensor=False)
            return test_embedding is not None
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
