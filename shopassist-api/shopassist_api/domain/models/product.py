from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
  id:str
  name:str
  description:str
  category:str
  price:float
  brand: str
  rating: float
  review_count: int
  product_url:Optional[str]
  image_url:Optional[str]
  category_full:Optional[list[str]]
  availability:Optional[str]
  

