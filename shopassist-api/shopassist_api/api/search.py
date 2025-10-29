from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from shopassist_api.application.interfaces.service_interfaces import ProductServiceInterface
from shopassist_api.application.interfaces.di_container import get_product_service
from shopassist_api.application.services.context_builder import ContextBuilder
from shopassist_api.application.services.query_processor import QueryProcessor
from shopassist_api.application.services.retrieval_service import RetrievalService
from shopassist_api.domain.models.product import Product
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

retrieval_service = RetrievalService()
query_processor = QueryProcessor()
context_builder = ContextBuilder()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: Optional[Dict] = None

class SearchResponse(BaseModel):
    query: str
    results: List[Dict]
    context: str
    query_type: str
    filters_applied: Dict



@router.post("/search/vector", response_model=SearchResponse)
async def vector_search(request: SearchRequest):
    """
    Perform vector similarity search
    """
    try:
        # Process query
        cleaned_query, extracted_filters = query_processor.process_query(request.query)
        
        # Merge filters
        filters = {**(request.filters or {}), **extracted_filters}
        
        # Classify query type
        query_type = query_processor.classify_query_type(request.query)
        
        # Retrieve
        if query_type == 'product':
            results = retrieval_service.retrieve_products(
                cleaned_query,
                request.top_k,
                filters
            )
            context = context_builder.build_product_context(results)
        else:
            results = retrieval_service.retrieve_knowledge_base(
                cleaned_query,
                request.top_k
            )
            context = context_builder.build_knowledge_base_context(results)
        
        return SearchResponse(
            query=request.query,
            results=results,
            context=context,
            query_type=query_type,
            filters_applied=filters
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/hybrid")
async def hybrid_search(request: SearchRequest):
    """
    Perform hybrid search (vector + keyword)
    """
    # For now, same as vector search
    # Can add keyword search logic later
    return await vector_search(request)

@router.get("/search/test")
async def test_retrieval():
    """
    Test retrieval with sample queries
    """
    test_queries = [
        "laptop for video editing under $1500",
        "wireless headphones",
        "what is the return policy"
    ]
    
    results = {}
    
    for query in test_queries:
        response = await vector_search(SearchRequest(query=query))
        results[query] = {
            "num_results": len(response.results),
            "query_type": response.query_type,
            "top_result": response.results[0] if response.results else None
        }
    
    return results