"""
Dependency injection container for the Shop Assistant API.
"""
from shopassist_api.application.interfaces.service_interfaces import ProductServiceInterface
from shopassist_api.infrastructure.services.cosmos_product_service import CosmosProductService
from shopassist_api.infrastructure.services.dump_product_service import DumpProductService
from shopassist_api.application.settings.config import settings
from shopassist_api.application.interfaces.service_interfaces import EmbeddingServiceInterface
from shopassist_api.infrastructure.services.openai_embedding_service import OpenAIEmbeddingService

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

    def setup_embedding_services(self):
        """Configure embedding service bindings."""
        if settings.embedding_provider == "azure_openai":
            self._services[EmbeddingServiceInterface] = OpenAIEmbeddingService

    def _setup_services(self):
        """Configure service bindings."""
        
        # HERE Define the service bindings
        # Bind the interface to the concrete implementation
        if settings.use_dump_service:
            self.setup_dump_services()
        else:
            self.setup_cosmos_services()

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
