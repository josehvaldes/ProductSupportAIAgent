
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from shopassist_api.infrastructure.services.cosmos_product_service import CosmosProductService
from shopassist_api.domain.models.product import Product

router = APIRouter()

class ProductResponse(BaseModel):
    """Product response model."""
    id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None


@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """
    Retrieve product details by product ID.
    """
    try:
        # product_service = CosmosService()
        # product = product_service.get_product_by_id(product_id)
        product:Product = { "id": "test123",
                            "title": "Test Product",
                            "description": "A product for testing", 
                            "category": "Testing", 
                            "price": "19.99", 
                            "brand": "TestBrand", 
                            "rating": "4.5", 
                            "review_count": "10", 
                            "product_url": "http://example.com/product/test123", 
                            "image_url": "http://example.com/product/test123/image.jpg",  
                            "category_full": "Testing/Unit Tests", 
                            "availability": "In Stock" }
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/search/category/{category}", response_model=List[Product])
async def search_products_by_category(category: str):
    """
    Search products by category.
    """
    try:
        product_service = CosmosProductService()
        products = product_service.search_products_by_category(category)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching products by category: {str(e)}")

@router.get("/products/search/price", response_model=List[Product])
async def search_products_by_price_range(min_price: float, max_price: float):
    """
    Search products within a price range.
    """
    if min_price < 0 or max_price < 0:
        raise HTTPException(status_code=400, detail="Price values must be non-negative")
    if min_price > max_price:
        raise HTTPException(status_code=400, detail="Minimum price cannot be greater than maximum price")
    
    try:
        product_service = CosmosProductService()
        products = product_service.search_products_by_price_range(min_price, max_price)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching products by price range: {str(e)}")

# Optional: Keep a general search endpoint for future complex queries
@router.get("/products/search", response_model=List[Product])
async def search_products_general(
    category: Optional[str] = None, 
    min_price: Optional[float] = None, 
    max_price: Optional[float] = None,
    name: Optional[str] = None
):
    """
    General product search with multiple optional filters.
    At least one search parameter must be provided.
    """
    if not any([category, min_price is not None, max_price is not None, name]):
        raise HTTPException(status_code=400, detail="At least one search parameter must be provided")
    
    try:
        product_service = CosmosProductService()
        
        # For now, handle simple cases - can be extended for complex multi-filter searches
        if category and not any([min_price is not None, max_price is not None, name]):
            products = product_service.search_products_by_category(category)
        elif min_price is not None and max_price is not None and not any([category, name]):
            if min_price > max_price:
                raise HTTPException(status_code=400, detail="Minimum price cannot be greater than maximum price")
            products = product_service.search_products_by_price_range(min_price, max_price)
        else:
            # For complex multi-filter searches, you'd implement a new service method
            raise HTTPException(status_code=501, detail="Multi-filter search not yet implemented")
        
        return products
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in product search: {str(e)}")