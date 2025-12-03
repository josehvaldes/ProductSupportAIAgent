"""
Dependency injection container for the Shop Assistant API.
"""


from shopassist_api.application.services.session_manager import SessionManager
from shopassist_api.infrastructure.services.redis_cache_service import RedisCacheService
from shopassist_api.infrastructure.services.cosmos_product_service import CosmosProductService
from shopassist_api.infrastructure.services.dumb_product_service import DumbProductService
from shopassist_api.infrastructure.services.milvus_service import MilvusService
from shopassist_api.infrastructure.services.openai_embedding_service import OpenAIEmbeddingService
from shopassist_api.infrastructure.services.openai_llm_service import OpenAILLMService
from shopassist_api.infrastructure.services.transformers_embedding_service import TransformersEmbeddingService
from shopassist_api.application.interfaces.service_interfaces import CacheServiceInterface, LLMServiceInterface, RepositoryServiceInterface, VectorServiceInterface
from shopassist_api.application.interfaces.service_interfaces import EmbeddingServiceInterface
from shopassist_api.application.services.retrieval_service import RetrievalService
from shopassist_api.application.services.comparison_service import ComparisonService
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
        self._services[RepositoryServiceInterface] = DumbProductService

    def setup_cosmos_services(self):
        """Configure BUMP service bindings."""
        self._services[RepositoryServiceInterface] = CosmosProductService


    def _setup_services(self):
        """Configure service bindings."""
        
        # HERE Define the service bindings
        # Bind the interface to the concrete implementation
        if settings.use_dumb_service:
            self.setup_dump_services()
        else:
            self.setup_cosmos_services()

        if settings.embedding_provider == "azure_openai":
            self._services[EmbeddingServiceInterface] = OpenAIEmbeddingService
        elif settings.embedding_provider == "transformers":
            self._services[EmbeddingServiceInterface] = TransformersEmbeddingService

        self._services[VectorServiceInterface] = MilvusService
        self._services[LLMServiceInterface] = OpenAILLMService
        self._services[CacheServiceInterface] = RedisCacheService

    def get_service(self, service_type, *args, **kwargs):
        
        # Return cached singleton if exists
        if service_type in self._singletons:
            return self._singletons[service_type]
        
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


def get_vector_service() -> VectorServiceInterface:
    """Dependency injection function for vector service."""
    return _container.get_service(VectorServiceInterface)

#TODO refactor and use self._services[''] mapping
def get_llm_service()->LLMServiceInterface:
    """Dependency injection function for LLM service."""
    return _container.get_service(LLMServiceInterface)

def get_nanolm_service():
    """Dependency injection function for nano LLM service."""
    return _container.get_service(LLMServiceInterface,
                                  model_name=settings.azure_openai_nano_model,
                                  deployment_name=settings.azure_openai_nano_model_deployment)

#TODO refactor and use self._services[''] mapping
def get_embedding_service() -> EmbeddingServiceInterface:
    """Dependency injection function for embedding service."""
    return _container.get_service(EmbeddingServiceInterface)

def get_category_embedding_service() -> EmbeddingServiceInterface:
    """Dependency injection function for category embedding service."""
    if settings.embedding_provider == "azure_openai":
        embedded_service = OpenAIEmbeddingService()
    elif settings.embedding_provider == "transformers":
        embedded_service = TransformersEmbeddingService(model_name=settings.transformers_category_embedding_model)

    return embedded_service

def get_retrieval_service():
    """Dependency injection function for retrieval service."""

    vector_service = get_vector_service()
    embedding_service = get_embedding_service()
    product_service = get_repository_service()
    category_embedder_service = get_category_embedding_service()
    return RetrievalService(
        vector_service=vector_service,
        embedding_service=embedding_service,
        repository_service=product_service,
        category_embedder_service=category_embedder_service
    )

def get_rag_service():
    """Dependency injection function for RAG service."""
    llm_service = get_llm_service()
    nanolm_service = get_nanolm_service()
    retrieval_service = get_retrieval_service()
    session_manager = get_session_manager()
    return RAGService(llm_service=llm_service, nanolm_service=nanolm_service, 
                      retrieval_service=retrieval_service, session_manager=session_manager)

def get_cache_service():
    """Dependency injection function for cache service."""
    return _container.get_service(CacheServiceInterface)

def get_session_manager():
    """Dependency injection function for context manager service."""
    repository = get_repository_service()
    cache = get_cache_service()
    return SessionManager( repository_service=repository, cache_service=cache)

def get_comparison_service():
    """Dependency injection function for comparison service."""
    repository = get_repository_service()
    llm_service = get_llm_service()
    return ComparisonService(repository_service=repository, llm_service=llm_service)