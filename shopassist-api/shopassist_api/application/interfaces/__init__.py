"""
Application interfaces module.
"""
from .service_interfaces import ProductServiceInterface
from .service_interfaces import EmbeddingServiceInterface
from .di_container import get_product_service

__all__ = ["ProductServiceInterface", "EmbeddingServiceInterface", "get_product_service"]