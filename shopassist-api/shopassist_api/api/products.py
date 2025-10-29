from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from shopassist_api.application.interfaces.service_interfaces import ProductServiceInterface
from shopassist_api.application.interfaces.di_container import get_product_service
from shopassist_api.domain.models.product import Product
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

# class ProductResponse(BaseModel):
#     """Product response model."""
#     id: str
#     name: str
#     description: Optional[str] = None
#     category: Optional[str] = None



@router.get("/products/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    product_service: ProductServiceInterface = Depends(get_product_service)
):
    """
    Retrieve product details by product ID.
    """
    try:
        product = await product_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/search/category/{category}", response_model=List[Product])
async def search_products_by_category(
    category: str,
    product_service: ProductServiceInterface = Depends(get_product_service)
):
    """
    Search products by category.
    """
    try:
        products = await product_service.search_products_by_category(category)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching products by category: {str(e)}")

@router.get("/products/search/price", response_model=List[Product])
async def search_products_by_price_range(
    min_price: float, 
    max_price: float,
    product_service: ProductServiceInterface = Depends(get_product_service)
):
    """
    Search products within a price range.
    """
    if min_price < 0 or max_price < 0:
        raise HTTPException(status_code=400, detail="Price values must be non-negative")
    if min_price > max_price:
        raise HTTPException(status_code=400, detail="Minimum price cannot be greater than maximum price")
    
    try:
        products = await product_service.search_products_by_price_range(min_price, max_price)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching products by price range: {str(e)}")

# Optional: Keep a general search endpoint for future complex queries
@router.get("/products/search", response_model=List[Product])
async def search_products_general(
    category: Optional[str] = None, 
    min_price: Optional[float] = None, 
    max_price: Optional[float] = None,
    name: Optional[str] = None,
    product_service: ProductServiceInterface = Depends(get_product_service)
):
    """
    General product search with multiple optional filters.
    At least one search parameter must be provided.
    """
    if not any([category, min_price is not None, max_price is not None, name]):
        raise HTTPException(status_code=400, detail="At least one search parameter must be provided")
    
    try:
        # For now, handle simple cases - can be extended for complex multi-filter searches
        if category and not any([min_price is not None, max_price is not None, name]):
            products = await product_service.search_products_by_category(category)
        elif min_price is not None and max_price is not None and not any([category, name]):
            if min_price > max_price:
                raise HTTPException(status_code=400, detail="Minimum price cannot be greater than maximum price")
            products = await product_service.search_products_by_price_range(min_price, max_price)
        else:
            # For complex multi-filter searches, you'd implement a new service method
            raise HTTPException(status_code=501, detail="Multi-filter search not yet implemented")
        
        return products
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in product search: {str(e)}")