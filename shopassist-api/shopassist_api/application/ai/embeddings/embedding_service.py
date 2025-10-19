"""
Text embeddings functionality for semantic search and similarity.
"""
import numpy as np
from typing import List, Optional, Dict, Any
from shopassist_api.application.ai.models.llm_client import LLMClient
from shopassist_api.application.settings.config import settings


class EmbeddingService:
    """
    Service for generating and managing text embeddings.
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.embedding_cache: Dict[str, List[float]] = {}
    
    async def generate_embedding(self, text: str, use_cache: bool = True) -> Optional[List[float]]:
        """
        Generate embedding for a given text.
        
        Args:
            text: Text to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            Embedding vector or None if error
        """
        if use_cache and text in self.embedding_cache:
            return self.embedding_cache[text]
        
        embedding = await self.llm_client.generate_embedding(text)
        
        if embedding and use_cache:
            self.embedding_cache[text] = embedding
        
        return embedding
    
    async def generate_batch_embeddings(
        self, 
        texts: List[str], 
        use_cache: bool = True
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for text in texts:
            embedding = await self.generate_embedding(text, use_cache)
            embeddings.append(embedding)
        
        return embeddings
    
    def cosine_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        
        except Exception:
            return 0.0
    
    async def find_most_similar(
        self, 
        query_text: str, 
        candidate_texts: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find the most similar texts to a query using embeddings.
        
        Args:
            query_text: Query text
            candidate_texts: List of candidate texts to compare
            top_k: Number of top results to return
            
        Returns:
            List of similar texts with similarity scores
        """
        # Generate query embedding
        query_embedding = await self.generate_embedding(query_text)
        if not query_embedding:
            return []
        
        # Generate candidate embeddings
        candidate_embeddings = await self.generate_batch_embeddings(candidate_texts)
        
        # Calculate similarities
        similarities = []
        for i, candidate_embedding in enumerate(candidate_embeddings):
            if candidate_embedding:
                similarity = self.cosine_similarity(query_embedding, candidate_embedding)
                similarities.append({
                    "text": candidate_texts[i],
                    "similarity": similarity,
                    "index": i
                })
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self.embedding_cache.clear()
