from pydantic import BaseModel

class Chunk(BaseModel):
  id:str
  product_id:str
  text:str
  embedding:str
  
  chunk_index:str
  total_chunks:str
  category:str
  price:str
  brand:str