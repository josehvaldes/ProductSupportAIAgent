"""
Dependency injection container for the Shop Assistant API.
"""

from shopassist_api.infrastructure.services.cosmos_product_service import CosmosProductService
from shopassist_api.infrastructure.services.dump_product_service import DumpProductService
from shopassist_api.infrastructure.services.milvus_service import MilvusService
from shopassist_api.infrastructure.services.openai_embedding_service import OpenAIEmbeddingService
from shopassist_api.infrastructure.services.openai_llm_service import OpenAILLMService
from shopassist_api.infrastructure.services.transformers_embedding_service import TransformersEmbeddingService
from shopassist_api.application.interfaces.service_interfaces import LLMServiceInterface, RepositoryServiceInterface, VectorServiceInterface
from shopassist_api.application.interfaces.service_interfaces import EmbeddingServiceInterface
from shopassist_api.application.services.rag_service import RAGService
from shopassist_api.application.settings.config import settings

class DIContainer:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services = {}
        self._singletons = {}
        self._setup_services()
    
    def setup_dump_services(self):
        """Configure BUMP service bindings."""
        self._services[RepositoryServiceInterface] = DumpProductService

    def setup_cosmos_services(self):
        """Configure BUMP service bindings."""
        self._services[RepositoryServiceInterface] = CosmosProductService


    def _setup_services(self):
        """Configure service bindings."""
        
        # HERE Define the service bindings
        # Bind the interface to the concrete implementation
        if settings.use_dump_service:
            self.setup_dump_services()
        else:
            self.setup_cosmos_services()

        print(f"Setting up Embedding Service for provider: {settings.embedding_provider}")

        if settings.embedding_provider == "azure_openai":
            self._services[EmbeddingServiceInterface] = OpenAIEmbeddingService
        elif settings.embedding_provider == "transformers":
            self._services[EmbeddingServiceInterface] = TransformersEmbeddingService

        self._services[VectorServiceInterface] = MilvusService
        self._services[LLMServiceInterface] = OpenAILLMService

    def get_service(self, service_type, *args, **kwargs):
        """Get a service instance by type."""
        if service_type in self._services:
            service_class = self._services[service_type]
            return service_class( *args, **kwargs)
        raise ValueError(f"Service {service_type} not registered")


# Global container instance
_container = DIContainer()


def get_repository_service() -> RepositoryServiceInterface:
    """Dependency injection function for product service."""
    return _container.get_service(RepositoryServiceInterface)

def get_embedding_service() -> EmbeddingServiceInterface:
    """Dependency injection function for embedding service."""
    return _container.get_service(EmbeddingServiceInterface)

def get_vector_service() -> VectorServiceInterface:
    """Dependency injection function for vector service."""
    return _container.get_service(VectorServiceInterface)

def get_llm_service():
    """Dependency injection function for LLM service."""
    return _container.get_service(LLMServiceInterface)

def get_retrieval_service():
    """Dependency injection function for retrieval service."""
    from shopassist_api.application.services.retrieval_service import RetrievalService
    vector_service = get_vector_service()
    embedding_service = get_embedding_service()
    product_service = get_repository_service()
    return RetrievalService(
        vector_service=vector_service,
        embedding_service=embedding_service,
        repository_service=product_service
    )

def get_rag_service():
    """Dependency injection function for RAG service."""

    llm_service = get_llm_service()
    retrieval_service = get_retrieval_service()
    return RAGService(llm_service=llm_service, retrieval_service=retrieval_service)
