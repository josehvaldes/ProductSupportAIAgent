"""
Product retrieval system for finding relevant products based on user queries.
"""
from typing import List, Dict, Any, Optional
from shopassist_api.core.config import settings
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

class ProductRetriever:
    """
    Retrieves relevant product information based on user queries.
    Uses Azure AI Search or similar vector search capabilities.
    """
    
    def __init__(self):
        self.search_client = None
        self._initialize_search_client()
    
    def _initialize_search_client(self):
        """Initialize Azure AI Search client."""
        try:
            if settings.azure_search_endpoint and settings.azure_search_key:
                
                self.search_client = SearchClient(
                    endpoint=settings.azure_search_endpoint,
                    index_name=settings.azure_search_index,
                    credential=AzureKeyCredential(settings.azure_search_key)
                )
        except ImportError:
            # Azure search not available
            self.search_client = None
        except Exception:
            # Configuration error
            self.search_client = None
    
    async def search(self, query: str, top_k: int = 5) -> str:
        """
        Search for relevant products based on the query.
        
        Args:
            query: User's search query
            top_k: Number of top results to return
            
        Returns:
            Formatted string with relevant product information
        """
        if not self.search_client:
            return await self._mock_search(query, top_k)
        
        try:
            # Perform semantic search
            results = self.search_client.search(
                search_text=query,
                top=top_k,
                search_mode="semantic",
                semantic_configuration_name="default"
            )
            
            # Format results
            formatted_results = []
            for result in results:
                product_info = {
                    "name": result.get("name", "Unknown Product"),
                    "description": result.get("description", ""),
                    "price": result.get("price", "N/A"),
                    "category": result.get("category", ""),
                    "availability": result.get("availability", "Unknown")
                }
                formatted_results.append(product_info)
            
            return self._format_products(formatted_results)
            
        except Exception as e:
            return await self._mock_search(query, top_k)
    
    async def _mock_search(self, query: str, top_k: int) -> str:
        """
        Mock search function for development/testing.
        """
        mock_products = [
            {
                "name": "Wireless Bluetooth Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": "$99.99",
                "category": "Electronics",
                "availability": "In Stock"
            },
            {
                "name": "Ergonomic Office Chair",
                "description": "Comfortable office chair with lumbar support",
                "price": "$299.99",
                "category": "Furniture",
                "availability": "In Stock"
            },
            {
                "name": "Smart Fitness Watch",
                "description": "Feature-rich smartwatch with health monitoring",
                "price": "$199.99",
                "category": "Electronics",
                "availability": "Limited Stock"
            }
        ]
        
        # Simple keyword matching for mock
        relevant_products = []
        query_lower = query.lower()
        
        for product in mock_products:
            if any(word in product["name"].lower() or word in product["description"].lower() 
                   for word in query_lower.split()):
                relevant_products.append(product)
        
        # Return top_k results
        return self._format_products(relevant_products[:top_k])
    
    def _format_products(self, products: List[Dict[str, Any]]) -> str:
        """
        Format product information for the AI model.
        """
        if not products:
            return "No specific products found for this query."
        
        formatted = "Here are some relevant products:\n\n"
        
        for i, product in enumerate(products, 1):
            formatted += f"{i}. **{product['name']}**\n"
            formatted += f"   - Description: {product['description']}\n"
            formatted += f"   - Price: {product['price']}\n"
            formatted += f"   - Category: {product['category']}\n"
            formatted += f"   - Availability: {product['availability']}\n\n"
        
        return formatted
