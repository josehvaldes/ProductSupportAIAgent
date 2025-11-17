import pytest
from shopassist_api.application.services.context_builder import ContextBuilder

class TestContextBuilder:
    def setup_method(self):
        self.builder = ContextBuilder()
    
    def test_build_product_context(self):
        results = [
            {"name": "Laptop A", "price": 999, "description": "Great laptop", 
             "category": "Electronics", "brand": "BrandX", "availability": "in_stock"}
        ]
        context = self.builder.build_product_context(results)
        assert "Laptop A" in context
        assert "999" in context

    def test_build_knowledge_base_context(self):
        chunks = [
            {"doc_type": "manual", "text": "This is a product manual."}
        ]
        context = self.builder.build_knowledge_base_context(chunks)
        assert "product manual" in context

