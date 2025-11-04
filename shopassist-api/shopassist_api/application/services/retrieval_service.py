from typing import List, Dict, Optional
from shopassist_api.application.interfaces.service_interfaces import EmbeddingServiceInterface, RepositoryServiceInterface, VectorServiceInterface
from shopassist_api.logging_config import get_logger
import traceback

logger = get_logger(__name__)


class RetrievalService:
    def __init__(self,
        vector_service: VectorServiceInterface,
        embedding_service: EmbeddingServiceInterface,
        repository_service: RepositoryServiceInterface):
        self.milvus = vector_service
        self.embedder = embedding_service
        self.cosmos = repository_service

    async def retrieve_top_categories(self, query:str, top_k=5) -> List[Dict]:
        """Retrieve product categories"""
        try:
            logger.info(f"Generating embedding for query: {query}")
            query_embedding = self.embedder.generate_embedding(query)
            categories = self.milvus.search_categories(
                query_embedding=query_embedding,
                top_k=top_k) # Get top category
            
            logger.info(f"Retrieved categories: {len(categories)}")
            if categories:
                return categories
            else:
                return {}
            
        except Exception as e:
            logger.error(f"Error retrieving categories: {e}")
            traceback.print_exc()
            return ""

    async def retrieve_products(
            self,
            query: str,
            top_k: int = 5,
            filters: Optional[Dict] = None,
            enriched: bool = True
        ) -> List[Dict]:
        """
        Retrieve relevant products using vector search
        
        Args:
            query: User query string
            top_k: Number of results to return
            filters: Optional filters (price, category, brand)
            
        Returns:
            List of relevant products with scores
        """
        try:
            # Generate query embedding
            logger.info(f"  Generating embedding for query: {query}")
            query_embedding = self.embedder.generate_embedding(query)
            
            # Build filter expression for Milvus
            filter_expr = self._build_filter_expression(filters)
            
            # Search in Milvus
            results = self.milvus.search_products(
                query_embedding=query_embedding,
                top_k=top_k, # * 2,  # Get more to deduplicate
                filters=filter_expr
            )            
            # Deduplicate by product_id and aggregate scores
            products = self._deduplicate_and_aggregate(results)
            logger.info(f"Retrieved {len(products)} unique products from Milvus")
            
            results_to_return = []
            # Enrich with full product data from Cosmos DB
            if enriched:
                results_to_return = await self._enrich_with_product_data(products)
            else:
                results_to_return = products

            # Limit to top_k
            return results_to_return[:top_k]
            
        except Exception as e:
            logger.error(f"Error in retrieve_products: {e}")
            traceback.print_exc()
            return []

    async def retrieve_knowledge_base(
            self,
            query: str,
            top_k: int = 3
        ) -> List[Dict]:
        """
        Retrieve relevant knowledge base chunks
        
        Args:
            query: User query string
            top_k: Number of chunks to return
            
        Returns:
            List of relevant KB chunks with scores
        """
        try:
            logger.info(f"Retrieving KB for query: {query}")
            
            # Generate query embedding
            query_embedding = self.embedder.generate_embedding(query)
            
            # Search knowledge base
            results = self.milvus.search_knowledge_base(
                query_embedding=query_embedding,
                top_k=top_k
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error in retrieve_knowledge_base: {e}")
            return []
    
    async def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        use_vector: bool = True,
        use_keyword: bool = False
    ) -> List[Dict]:
        """
        Combine vector and keyword search results
        
        For now, focuses on vector search.
        Keyword search via Cosmos DB can be added later.
        """
        if use_vector:
            return self.retrieve_products(query, top_k)
        else:
            # Fallback to Cosmos DB keyword search
            return await self.cosmos.search_products_by_text(query, top_k)
    
    def _build_filter_expression(self, filters: Optional[Dict]) -> Optional[str]:
        """
        Build Milvus filter expression from filters dict
        
        Example filters:
        {
            "min_price": 100,
            "max_price": 500,
            "category": "Laptops",
            "brand": "Apple"
        }
        
        Returns Milvus expression: "price >= 100 and price <= 500 and category == 'Laptops'"
        """
        if not filters:
            return None
        
        expressions = []
        
        if "min_price" in filters:
            expressions.append(f"price >= {filters['min_price']}")
        
        if "max_price" in filters:
            expressions.append(f"price <= {filters['max_price']}")
        
        if "category" in filters:
            expressions.append(f"category == '{filters['category']}'")
        
        if "brand" in filters:
            expressions.append(f"brand == '{filters['brand']}'")
        
        return " and ".join(expressions) if expressions else None
    
    def _deduplicate_and_aggregate(self, results: List[Dict]) -> List[Dict]:
        """
        Deduplicate chunks from same product and aggregate scores
        
        Takes best score for each product
        """
        product_map = {}
        
        for result in results:
            product_id = result['product_id']
            
            if product_id not in product_map:
                product_map[product_id] = result
            else:
                # Keep result with better score (higher distance in COSINE)
                if result['distance'] > product_map[product_id]['distance']:
                    product_map[product_id] = result
        
        # Sort by score
        products = list(product_map.values())
        products.sort(key=lambda x: x['distance'], reverse=True)
        
        return products
    
    async def _enrich_with_product_data(self, products: List[Dict]) -> List[Dict]:
        """
        Fetch full product details from Cosmos DB
        """
        enriched = []
        logger.info(f"Enriching {len(products)} products with full data from Cosmos DB")

        for product in products:
            try:
                # Get full product from Cosmos
                logger.info(f"Fetching product ID: {product['product_id']}")
                full_product = await self.cosmos.get_product_by_id(product['product_id'])
                if full_product:
                    enriched.append({
                        **full_product,
                        "relevance_score": product['distance'],
                        "matched_text": product['text'][:200]  # Preview
                    })
            except Exception as e:
                logger.error(f"Error enriching product {product['product_id']}: {e}")
                traceback.print_exc()
                continue

        return enriched
    
    async def health_check(self) -> dict:
        """Ping the service to check connectivity"""
        try:
            vector_healthy = await self.milvus.health_check()
            embedding_healthy = await self.embedder.health_check()
            repository_healthy = await self.cosmos.health_check()
            
            return {
                "vector_service": "healthy" if vector_healthy else "unhealthy",
                "embedding_service": "healthy" if embedding_healthy else "unhealthy",
                "repository_service": "healthy" if repository_healthy else "unhealthy"
            }
        except Exception as e:
            return {
                "error": str(e)
            }