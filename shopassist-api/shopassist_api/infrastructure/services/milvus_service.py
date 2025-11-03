from typing import List, Dict, Optional
from pymilvus import connections, Collection
from shopassist_api.application.interfaces.service_interfaces import VectorServiceInterface
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

class MilvusService(VectorServiceInterface):
    """Service to interact with Milvus vector database."""
    def __init__(self, host: str = "localhost", port: str = "19530"):
        self.host = host
        self.port = port
        self.connected = False
        self._connect()

    def _connect(self):
        """Connect to Milvus"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            connected = False
            #raise
    
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
    
    def search_products(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[str] = None
    ) -> List[Dict]:
        """Search products by vector similarity"""
        collection = Collection("products_collection")
        collection.load()
        
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 64}  # Search depth
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
    
    def search_knowledge_base(
        self,
        query_embedding: List[float],
        top_k: int = 3
    ) -> List[Dict]:
        """Search knowledge base by vector similarity"""
        collection = Collection("knowledge_base_collection")
        collection.load()
        
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 64}
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
