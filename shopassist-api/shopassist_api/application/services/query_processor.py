import re
from typing import Dict, Tuple
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

class QueryProcessor:
    """
    Process and enhance user queries for better retrieval
    """
    
    # Price patterns
    PRICE_PATTERNS = [
        r'under \$?(\d+)',
        r'less than \$?(\d+)',
        r'below \$?(\d+)',
        r'cheaper than \$?(\d+)',
        r'between \$?(\d+) and \$?(\d+)',
        r'\$?(\d+) to \$?(\d+)',
    ]
    
    # Policy keywords
    POLICY_KEYWORDS = [
        'return', 'refund', 'shipping', 'delivery',
        'warranty', 'guarantee', 'policy', 'exchange'
    ]
    
    def process_query(self, query: str) -> Tuple[str, Dict]:
        """
        Process query and extract filters
        
        Returns:
            Tuple of (cleaned_query, filters)
        """
        query_lower = query.lower()
        filters = {}
        
        # Extract price filters
        price_filter = self._extract_price_filter(query_lower)
        if price_filter:
            filters.update(price_filter)
        
        # Clean query (remove filter text)
        cleaned_query = self._clean_query(query)
        
        logger.info(f"Processed query: '{cleaned_query}' | Filters: {filters}")
        
        return cleaned_query, filters
    
    @DeprecationWarning
    def classify_query_type(self, query: str) -> str:
        """
        Classify if query is about products or policies
        
        Returns:
            'product' or 'policy'
        """
        query_lower = query.lower()
        
        # Check for policy keywords
        if any(keyword in query_lower for keyword in self.POLICY_KEYWORDS):
            return 'policy'
        
        return 'product'
    
    def _extract_price_filter(self, query: str) -> Dict:
        """Extract price range from query"""
        filters = {}
        
        # Try each pattern
        for pattern in self.PRICE_PATTERNS:
            match = re.search(pattern, query)
            if match:
                if 'between' in pattern or 'to' in pattern:
                    # Range
                    filters['min_price'] = float(match.group(1))
                    filters['max_price'] = float(match.group(2))
                else:
                    # Max price only
                    filters['max_price'] = float(match.group(1))
                break
        
        return filters
    
    
    def _clean_query(self, query: str) -> str:
        """Remove filter expressions from query"""
        # Remove price expressions
        for pattern in self.PRICE_PATTERNS:
            query = re.sub(pattern, '', query, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        return query.strip()