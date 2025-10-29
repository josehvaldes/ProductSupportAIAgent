"""
Dependency injection container for the Shop Assistant API.
"""
from shopassist_api.application.interfaces.service_interfaces import ProductServiceInterface, VectorServiceInterface
from shopassist_api.infrastructure.services.cosmos_product_service import CosmosProductService
from shopassist_api.infrastructure.services.dump_product_service import DumpProductService
from shopassist_api.application.settings.config import settings
from shopassist_api.application.interfaces.service_interfaces import EmbeddingServiceInterface
from shopassist_api.infrastructure.services.milvus_service import MilvusService
from shopassist_api.infrastructure.services.openai_embedding_service import OpenAIEmbeddingService
from shopassist_api.infrastructure.services.transformers_embedding_service import TransformersEmbeddingService

class DIContainer:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services = {}
        self._setup_services()
    
    def setup_dump_services(self):
        """Configure BUMP service bindings."""
        self._services[ProductServiceInterface] = DumpProductService

    def setup_cosmos_services(self):
        """Configure BUMP service bindings."""
        self._services[ProductServiceInterface] = CosmosProductService


    def _setup_services(self):
        """Configure service bindings."""
        
        # HERE Define the service bindings
        # Bind the interface to the concrete implementation
        if settings.use_dump_service:
            self.setup_dump_services()
        else:
            self.setup_cosmos_services()
        
        if settings.embedding_provider == "azure_openai":
            self._services[EmbeddingServiceInterface] = OpenAIEmbeddingService
        elif settings.embedding_provider == "transformers":
            self._services[EmbeddingServiceInterface] = TransformersEmbeddingService

        self._services[VectorServiceInterface] = MilvusService

    def get_service(self, service_type):
        """Get a service instance by type."""
        if service_type in self._services:
            service_class = self._services[service_type]
            return service_class()
        raise ValueError(f"Service {service_type} not registered")


# Global container instance
_container = DIContainer()


def get_product_service() -> ProductServiceInterface:
    """Dependency injection function for product service."""
    return _container.get_service(ProductServiceInterface)

def get_embedding_service() -> EmbeddingServiceInterface:
    """Dependency injection function for embedding service."""
    return _container.get_service(EmbeddingServiceInterface)

def get_vector_service() -> VectorServiceInterface:
    """Dependency injection function for vector service."""
    return _container.get_service(VectorServiceInterface)
