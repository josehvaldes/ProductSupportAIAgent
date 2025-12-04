import json
from typing import List, Dict, Optional
from langsmith import traceable
from shopassist_api.application.interfaces.service_interfaces import EmbeddingServiceInterface, RepositoryServiceInterface, VectorServiceInterface
from shopassist_api.application.settings.config import settings
from shopassist_api.logging_config import get_logger
import traceback
import numpy as np
from numpy import dot
from numpy.linalg import norm

logger = get_logger(__name__)


class RetrievalService:
    def __init__(self,
        vector_service: VectorServiceInterface,
        embedding_service: EmbeddingServiceInterface,
        repository_service: RepositoryServiceInterface,
        category_embedder_service: EmbeddingServiceInterface
        ):
        self.milvus = vector_service
        self.embedder = embedding_service
        self.cosmos = repository_service
        self.category_embedder = category_embedder_service

    def cosine_sim(self, a, b):
        return dot(a, b) / (norm(a) * norm(b))

    @traceable(name="retrieval.retrieve_top_categories", tags=["retrieval", "category", "milvus"], metadata={"version": "1.0"})
    async def retrieve_top_categories(self, query:str, top_k=3) -> List[Dict]:
        """Retrieve product categories"""
        try:
            logger.info(f"Generating embedding for query: {query}")
            query_embedding = await self.category_embedder.generate_embedding(query)
            categories = self.milvus.search_categories(
                query_embedding=query_embedding,
                field="embedding",
                top_k=top_k) # Get top category
            
            categories_sim = []
            for cat in categories:
                sim_short = self.cosine_sim(query_embedding, cat['embedding'])
                sim_full = self.cosine_sim(query_embedding, cat['full_embedding'])
                val = {
                    "id": cat['id'],
                    "name": cat['name'],
                    "full_name": cat['full_name'],
                    "distance": cat['distance'],
                    "sim_short": sim_short,
                    "sim_full": sim_full,
                    "score": 0.7*sim_full + 0.3*sim_short # Weighted score
                }
                categories_sim.append(val)

            categories_with_full = self.milvus.search_categories(
                query_embedding=query_embedding,
                field="full_embedding",
                top_k=top_k) # Get top category            
            
            categories_sim_full = []
            for cat in categories_with_full:
                sim_short = self.cosine_sim(query_embedding, cat['embedding'])
                sim_full = self.cosine_sim(query_embedding, cat['full_embedding'])
                val = {
                    "id": cat['id'],
                    "name": cat['name'],
                    "full_name": cat['full_name'],
                    "distance": cat['distance'],
                    "sim_short": sim_short,
                    "sim_full": sim_full,
                    "score": 0.7*sim_full + 0.3*sim_short # Weighted score
                }
                categories_sim_full.append(val)

            #merge and deduplicate categories
            categories = self.merge_deduplicate_categories(categories_sim, categories_sim_full)

            if categories:
                return categories[:top_k]
            else:
                return {}
            
        except Exception as e:
            logger.error(f"Error retrieving categories: {e}")
            traceback.print_exc()
            return ""

    def merge_deduplicate_categories(self, categories1: List[Dict], categories2: List[Dict]) -> List[Dict]:
        """Merge and deduplicate categories from two lists"""
        category_map = {}
        for cat in categories1 + categories2:
            cat_id = cat['id']
            if cat_id not in category_map:
                category_map[cat_id] = cat
            else:
                # Keep the one with better score
                if cat['distance'] > category_map[cat_id]['score']:
                    category_map[cat_id] = cat
        #sorted by distance
        sorted_categories = sorted(category_map.values(), key=lambda x: x['score'], reverse=True)
        return sorted_categories

    @traceable(name="retrieval.retrieve_products_adaptative", tags=["retrieval", "product", "milvus"], metadata={"version": "1.0"})
    async def retrieve_products_adaptative(
            self,
            query: str,
            top_k: int = 3,
            filters: Optional[Dict] = None,
            enriched: bool = True
        ) -> List[Dict]:
        """
        Retrieve relevant products using vector search with adaptative thresholds
        top_k: should be 2 or higher for adaptative filtering to work properly
        """
        try:
            # Generate query embedding
            query_embedding = await self.embedder.generate_embedding(query)
            # Build filter expression for Milvus
            filter_expr = self._build_filter_expression(filters)
            
            logger.info(f"Retrieve products for [{query}] and filters: {filter_expr}, Top_k:{top_k}, with adaptative filtering")
            # Search in Milvus with initial radius
            results = []

            #results with radius filtering
            results = self.milvus.search_products(
                    query_embedding=query_embedding,
                    top_k=top_k,
                    filters=filter_expr,
                    radius=settings.threshold_product_similarity
                )
            
            logger.info(f"Initial retrieved {len(results)} products for query: [{query}] with radius: {radius}")
            if len(results) == 0:
                # No results found. End
                return []
            
            # Adaptative filtering based on score distribution
            scores = [res['distance'] for res in results]
            if len(scores) > 1 and (scores[0] - scores[1]) > 0.15:
                results = results[:1]  # Keep only top 1 if big gap
                products = self._process_products(enriched, results)
                return products

            if np.std(scores) < 0.05:
                threshold = 0.15 + settings.threshold_product_similarity  # Stricter for uncertain cases
            else:
                threshold = 0.05 + settings.threshold_product_similarity  # Standard threshold.
            filtered_results = [res for res in results if res['distance'] >= threshold]
            if len(filtered_results) == 0:
                return []

            return await self._process_products(enriched, filtered_results)

        except Exception as e:
            logger.error(f"Error in retrieve_products: {e}")
            traceback.print_exc()
            return []

    async def _process_products(self, enriched:bool, products: List[Dict]) -> List[Dict]:
        """Placeholder for enriching products with full data"""
        # Deduplicate by product_id and aggregate scores
        products = self._deduplicate_and_aggregate(products)
        results_to_return = []
        # Enrich with full product data from Cosmos DB
        if enriched:
            results_to_return = await self._enrich_with_product_data(products)
            results_to_return.sort(key=lambda x: x['relevance_score'], reverse=True)
        else:
            products.sort(key=lambda x: x['distance'], reverse=True)
            results_to_return = products
            
        return results_to_return

    @traceable(name="retrieval.retrieve_products", tags=["retrieval", "product", "milvus"], metadata={"version": "1.0"})
    async def retrieve_products(
            self,
            query: str,
            top_k: int = 3,
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
            
            query_embedding = await self.embedder.generate_embedding(query)
            # Build filter expression for Milvus
            filter_expr = self._build_filter_expression(filters)
            
            logger.info(f"Retrieve products for {query} and filters: {filter_expr}")
            # Search in Milvus
            results = self.milvus.search_products(
                query_embedding=query_embedding,
                top_k=top_k,
                filters=filter_expr
            )            
            
            if len(results) == 0:
                # No results found
                return []
            
            return await self._process_products(enriched, results)
            
        except Exception as e:
            logger.error(f"Error in retrieve_products: {e}")
            traceback.print_exc()
            return []

    @traceable(name="retrieval.retrieve_knowledge_base", tags=["retrieval", "knowledge_base", "milvus"], metadata={"version": "1.0"})
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
            query_embedding = await self.embedder.generate_embedding(query)
            
            # Search knowledge base
            results = self.milvus.search_knowledge_base(
                query_embedding=query_embedding,
                top_k=top_k
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error in retrieve_knowledge_base: {e}")
            return []

    @traceable(name="retrieval.hybrid_search", tags=["retrieval", "product", "milvus"], metadata={"version": "1.0"})
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
        
        # Categorical filters
        if "category" in filters:
            expressions.append(f"category == '{filters['category']}'")

        if "categories" in filters:
            category_list = filters['categories']
            if category_list and isinstance(category_list, list) and len(category_list) > 0:
                category_expr = " or ".join([f"category == '{cat}'" for cat in category_list])
                expressions.append(f"({category_expr})")
        
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
        
        return products
    
    async def _enrich_with_product_data(self, products: List[Dict]) -> List[Dict]:
        """
        Fetch full product details from Cosmos DB
        """
        logger.info(f"Enriching {len(products)} products with full data from Cosmos DB")
        enriched = []
        if not products or len(products) == 0:
            return enriched
        product_ids = [product['product_id'] for product in products]
        try:
            full_products = await self.cosmos.get_products_by_ids(product_ids)
            for full_product in full_products:
                product = next((p for p in products if p['product_id'] == full_product['id']), None)
                if product:
                    enriched.append({
                        **full_product,
                        "relevance_score": product['distance'],
                        "matched_text": product['text'][:200]  # Preview
                    })
                else:
                    logger.warning(f"Product ID {full_product['id']} not found in Milvus-Cosmos results")
        except Exception as e:
            logger.error(f"Error enriching product {full_product['product_id']}: {e}")
            traceback.print_exc()

        return enriched
    
    async def health_check(self) -> dict:
        """Ping the service to check connectivity"""
        try:
            vector_healthy = await self.milvus.health_check()
            embedding_healthy = await self.embedder.health_check()
            
            return {
                "is_healthy": "healthy" if vector_healthy and embedding_healthy else "unhealthy",
                "vector_service": "healthy" if vector_healthy else "unhealthy",
                "embedding_service": "healthy" if embedding_healthy else "unhealthy",
            }
        except Exception as e:
            return {
                "error": str(e)
            }