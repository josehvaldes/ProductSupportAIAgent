"""
Test dependency injection implementation.
"""
import pytest
from unittest.mock import MagicMock
from shopassist_api.application.interfaces.service_interfaces import RepositoryServiceInterface
from shopassist_api.application.interfaces.di_container import get_repository_service
from shopassist_api.infrastructure.services.cosmos_product_service import CosmosProductService


def test_product_service_interface():
    """Test that CosmosProductService implements RepositoryServiceInterface."""
    service = CosmosProductService()
    assert isinstance(service, RepositoryServiceInterface)


def test_dependency_injection_container():
    """Test that the DI container returns the correct service."""
    service = get_repository_service()
    assert isinstance(service, RepositoryServiceInterface)
    assert isinstance(service, CosmosProductService)


def test_product_service_methods_exist():
    """Test that the service has all required methods."""
    service = get_repository_service()
    
    # Check that all abstract methods are implemented
    assert hasattr(service, 'get_product_by_id')
    assert hasattr(service, 'search_products_by_category')
    assert hasattr(service, 'search_products_by_price_range')
    
    # Check that methods are callable
    assert callable(service.get_product_by_id)
    assert callable(service.search_products_by_category)
    assert callable(service.search_products_by_price_range)
