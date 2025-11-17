import pytest
from shopassist_api.application.services.query_processor import QueryProcessor

class TestQueryProcessor:
    def setup_method(self):
        self.processor = QueryProcessor()
    
    def test_extract_price_filters(self):
        query = "laptop under $500"
        cleaned, filters = self.processor.process_query(query)
        assert filters['max_price'] == 500
        assert 'laptop' in cleaned
    
    def test_no_price_filters(self):
        query = "gaming laptop"
        cleaned, filters = self.processor.process_query(query)
        assert filters == {}
        assert cleaned == "gaming laptop"
    
    def test_between_price_filter(self):
        query = "smartphone between $200 and $400"
        cleaned, filters = self.processor.process_query(query)
        assert filters['min_price'] == 200
        assert filters['max_price'] == 400
        assert 'smartphone' in cleaned


