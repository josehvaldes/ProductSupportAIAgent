from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from shopassist_api.domain.models.message import Message
from shopassist_api.domain.models.user_preferences import UserPreferences

class SessionContext(BaseModel):
  """Data model for a chat session context"""
  id: str
  user_id: str
  created_at: datetime
  updated_at: datetime
  messages: List[Message]
  user_preferences: Optional[UserPreferences] 
  current_intent: Optional[str]
  metadata: dict  # user_agent, ip, etc.