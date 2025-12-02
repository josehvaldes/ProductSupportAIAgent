from typing import List, Dict, Optional
from langsmith import traceable
from pymilvus import connections, Collection
from shopassist_api.application.interfaces.service_interfaces import VectorServiceInterface
from shopassist_api.logging_config import get_logger
from shopassist_api.application.settings.config import settings

logger = get_logger(__name__)

class MilvusService(VectorServiceInterface):
    """Service to interact with Milvus vector database."""
    def __init__(self, host: str = None, port: str = None):
        self.host = host or settings.milvus_host
        self.port = port or settings.milvus_port
        self.connected = False
        self._connect()

    def _connect(self):
        """Connect to Milvus (reuses existing connection if available)"""
        try:
            # Check if already connected
            if connections.has_connection(alias="default"):
                logger.info(f"Using existing Milvus connection")
                self.connected = True
                return
            
            # Create new connection
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            self.connected = True
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            self.connected = False
    
    def insert_products(self, products: List[Dict]) -> int:
        """Insert product embeddings into Milvus"""
        collection = Collection("products_collection")
        
        # Prepare data for insertion
        data = [
            [p["id"] for p in products],  # id
            [p["product_id"] for p in products],  # product_id
            [p["text"] for p in products],  # text
            [p["embedding"] for p in products],  # embedding
            [p["chunk_index"] for p in products],  # chunk_index
            [p["total_chunks"] for p in products],  # total_chunks
            [p["category"] for p in products],  # category
            [p["price"] for p in products],  # price
            [p["brand"] for p in products]  # brand
        ]
        
        # Insert
        mr = collection.insert(data)
        collection.flush()
        logger.info(f"Inserted {len(products)} product chunks")
        return mr.insert_count

    def insert_knowledge_base(self, chunks: List[Dict]) -> int:
        """Insert knowledge base chunks into Milvus"""
        collection = Collection("knowledge_base_collection")
        
        data = [
            [c["id"] for c in chunks],
            [c["doc_id"] for c in chunks],
            [c["text"] for c in chunks],
            [c["chunk_index"] for c in chunks],
            [c["embedding"] for c in chunks],
            [c["doc_type"] for c in chunks]
        ]
        
        mr = collection.insert(data)
        collection.flush()
        logger.info(f"Inserted {len(chunks)} knowledge base chunks")
        return mr.insert_count
    
    def insert_categories(self, categories: List[Dict]) -> int:
        """Insert category embeddings into Milvus"""
        collection = Collection("categories_collection")
        
        data = [
            [c["id"] for c in categories],
            [c["name"] for c in categories],
            [c["full_name"] for c in categories],
            [c["embedding"] for c in categories],
            [c["full_embedding"] for c in categories]
        ]
        
        mr = collection.insert(data)
        collection.flush()
        logger.info(f"Inserted {len(categories)} categories")
        return mr.insert_count

    @traceable(name="milvus.search_products", tags=["retrieval", "products", "embedding", "milvus"], metadata={"version": "1.0"})
    def search_products(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[str] = None,
        radius: Optional[float] = None
    ) -> List[Dict]:
        """Search products by vector similarity"""
        collection = Collection("products_collection")
        collection.load()
        
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 128, 
                       "radius": radius if radius else settings.threshold_product_similarity
                       }
        }
        
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            
            param=search_params,
            limit=top_k,
            expr=filters,  # e.g., "price < 1000"
            output_fields=["product_id", "text", "category", "price", "brand"]
        )
        
        # Format results
        formatted = []
        for hits in results:
            for hit in hits:
                formatted.append({
                    "id": hit.id,
                    "distance": hit.distance,
                    "product_id": hit.entity.get("product_id"),
                    "text": hit.entity.get("text"),
                    "category": hit.entity.get("category"),
                    "price": hit.entity.get("price"),
                    "brand": hit.entity.get("brand")
                })
        
        return formatted

    @traceable(name="milvus.search_knowledge_base", tags=["retrieval", "knowledge_base", "embedding", "milvus"], metadata={"version": "1.0"})
    def search_knowledge_base(
        self,
        query_embedding: List[float],
        top_k: int = 3,
        radius: Optional[float] = None
    ) -> List[Dict]:
        """Search knowledge base by vector similarity"""
        collection = Collection("knowledge_base_collection")
        collection.load()
        
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 64, "radius": radius if radius else settings.threshold_knowledge_base_similarity}
        }
        
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["doc_id", "text", "doc_type"]
        )
        
        formatted = []
        for hits in results:
            for hit in hits:
                formatted.append({
                    "id": hit.id,
                    "distance": hit.distance,
                    "doc_id": hit.entity.get("doc_id"),
                    "text": hit.entity.get("text"),
                    "doc_type": hit.entity.get("doc_type")
                })
        
        return formatted

    @traceable(name="milvus.search_categories", tags=["retrieval", "categories", "embedding", "milvus"], metadata={"version": "1.0"})
    def search_categories(
        self,
        query_embedding: List[float],
        field: str = "embedding",
        top_k: int = 5) -> List[Dict]:
        """Search categories by vector similarity"""
        collection = Collection("categories_collection")
        collection.load()
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 64}
        }
        results = collection.search(
            data=[query_embedding],
            anns_field=field,
            param=search_params,
            limit=top_k,
            output_fields=["name", "full_name", "embedding", "full_embedding"]
        )
        formatted = []
        for hits in results:
            for hit in hits:
                formatted.append({
                    "id": hit.id,
                    "distance": hit.distance,
                    "name": hit.entity.get("name"),
                    "full_name": hit.entity.get("full_name"),
                    "embedding": hit.entity.get("embedding"),
                    "full_embedding": hit.entity.get("full_embedding")
                })

        return formatted

    def get_collection_stats(self, collection_name: str) -> Dict:
        """Get collection statistics"""
        collection = Collection(collection_name)
        
        return {
            "name": collection_name,
            "num_entities": collection.num_entities,
            "description": collection.description
        }
    
    async def health_check(self) -> bool:
        """Ping the service to check connectivity"""
        try:
            return connections.has_connection(alias="default")
        except Exception as e:
            logger.error(f"Milvus health check failed: {e}")
            return False
