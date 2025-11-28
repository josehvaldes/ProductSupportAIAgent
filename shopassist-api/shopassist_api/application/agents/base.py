from pydantic import BaseModel
from typing import Literal, Optional

class Metadata(BaseModel):
    """Metadata common to all agents"""
    id:str = ""
    input_token:int
    output_token:int
    total_token:int

class AgentResponse(BaseModel):
    """Base class for all agent responses"""
    agent_name: str
    message: str
    confidence: float = 0.0
    metadata: Metadata = None

class ProductSearchResponse(AgentResponse):
    """Structured response from ProductSearchAgent"""
    sources: list[dict] = []

class PolicyResponse(AgentResponse):
    """Structured policy agent response"""
    sources: list[str]
    needs_escalation: bool

class RouteDecision(BaseModel):
    """Structured output for routing"""
    agent: Literal["policy", "product_search", "product_detail", "comparison", "escalation"]
    confidence: float
    reasoning: str

class RouteDecisionResponse(BaseModel):
    agent: str
    confidence: float
    reasoning: str
    metadata:Optional[Metadata] = None

class EscalationResponse(AgentResponse):
    """Structured response from EscalationAgent"""
    ticket_id: str
    contact_info: str