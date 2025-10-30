from pydantic import BaseModel

class Session(BaseModel):
  id:str
  user_id:str
  session_id:str
  role:str
  content:str
  timestamp:str
  metadata:dict
