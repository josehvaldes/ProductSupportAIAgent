from pydantic import BaseModel

class Session(BaseModel):
  id:str
  product_id:str
  text:str
