from typing import List, Optional, Tuple

from pydantic import BaseModel


class UserPreferences(BaseModel):
    """Data model for user preferences"""
    price_range: Optional[Tuple[float, float]]
    preferred_categories: List[str]
    preferred_brands: List[str]
    mentioned_products: List[str]  # product_ids from conversation
