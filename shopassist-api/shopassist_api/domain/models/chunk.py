from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class KnowledgeBaseChunkModel(BaseModel):
    id: str = Field(..., description="Unique identifier for the chunk")
    knowledge_base_id: str = Field(..., description="Identifier of the associated knowledge base")
    chunk_text: str = Field(..., description="Text content of the chunk")
    embedding: List[float] = Field(None, description="Vector embedding of the chunk text")
    
    def to_milvus_dict(self) -> dict:
        """Convert the model to a dictionary suitable for Milvus insertion."""
        milvus_dict = self.dict()
        return milvus_dict

    @field_validator('embedding')
    def validate_embedding_dimension(cls, v):
        expected_dimension = 1536  # Example dimension, adjust as needed
        if v is not None and len(v) != expected_dimension:
            raise ValueError(f"Embedding must be of dimension {expected_dimension}, got {len(v)}")
        return v


class ProductChunkModel(BaseModel):
    id: str = Field(..., description="Unique identifier for the chunk")
    product_id: str = Field(..., description="Identifier of the associated product")
    chunk_text: str = Field(..., description="Text content of the chunk")
    embedding: list[float] = Field(None, description="Vector embedding of the chunk text")

    chunk_index: int = Field(..., description="Chunk order index")
    total_chunks: int = Field(..., description="Total chunks for product")
    category: str = Field(..., description="Product category")
    price: float = Field(..., description="Product price")
    brand: str = Field(..., description="Product brand")

    @field_validator('embedding')
    def validate_embedding_dimension(cls, v):
        #update for the right embedding dimension.  1536 for OpenAI ada-002 and text-embedding-3-small
        # 768 for miniLM
        if len(v) != 1536 and len(v) != 768:
            raise ValueError(f"Embedding must be 1536 dimensions, got {len(v)}")
        return v
    
    @field_validator('embedding')
    def validate_no_nan(cls, v):
        if any(x != x for x in v):  # Check for NaN
            raise ValueError("Embedding contains NaN values")
        return v