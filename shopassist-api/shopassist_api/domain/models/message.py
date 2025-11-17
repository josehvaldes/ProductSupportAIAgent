from pydantic import BaseModel

class Message(BaseModel):
  """Data model for a chat message"""
  id:str
  user_id:str
  session_id:str
  role:str
  content:str
  timestamp:str
  metadata:dict
