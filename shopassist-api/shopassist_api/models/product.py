from pydantic import BaseModel

class Product(BaseModel):
  id:str
  title:str
  description:str
  category:str
  price:str
  brand:str
  rating:str
  review_count:str
  product_url:str
  image_url:str
  category_full:str
  availability:str

