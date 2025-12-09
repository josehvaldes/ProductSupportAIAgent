import re
from typing import Dict, Tuple
from langsmith import traceable
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

        r'around \$?(\d+)',
        r'about \$?(\d+)',
        r'max \$?(\d+)',
        r'maximum \$?(\d+)',
        r'up to \$?(\d+)',
        r'not more than \$?(\d+)',
        r'budget of \$?(\d+)',
        r'afford \$?(\d+)',
        r'within \$?(\d+)',
    ]
    
    @traceable(name="query.process_query", tags=["query", "preprocessing"], metadata={"version": "1.0"})
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