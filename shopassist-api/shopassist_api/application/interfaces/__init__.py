"""
Application interfaces module.
"""
from .product_service_interface import ProductServiceInterface
from .di_container import get_product_service

__all__ = ["ProductServiceInterface", "get_product_service"]