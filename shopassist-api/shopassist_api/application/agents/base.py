from pydantic import BaseModel, Field
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
    sources: list[dict] = []


class PolicyResponse(AgentResponse):
    """Structured policy agent response"""
    sources: list[str]
    needs_escalation: bool

class RouteDecision(BaseModel):
    """Structured output for routing"""
    query: str = Field(
        description="The cleaned, specific sub-query to execute"
    )
    
    intent: Literal["policy", "product_search", "product_detail", "comparison", "escalation"] = Field(
        description="The intent category for this sub-query"
    )

class RouteRequest(BaseModel):
    """Complete routing decision with reasoning"""
    reasoning: str =  Field(
        description="Brief explanation of how the query was analyzed and decomposed"
    )
    routes: list[RouteDecision] =  Field(
        description="List of sub-queries to execute (1 for single-intent, 2+ for multi-intent)"
    )


class RouteDecisionResponse(BaseModel):
    agent: str
    reasoning: str
    routes : list[RouteDecision]
    metadata:Optional[Metadata] = None

class EscalationResponse(AgentResponse):
    """Structured response from EscalationAgent"""
    ticket_id: str
    contact_info: str

class AgentDecision(BaseModel):
    """Structured output for query processing decision"""
    results: Optional[list[str]] = None
    reasoning: Optional[str] = None

class PriceFilter(BaseModel):
    """Extracted price range from user query"""
    min_price: Optional[float] = Field(None, description="Minimum price in USD")
    max_price: Optional[float] = Field(None, description="Maximum price in USD")
    confidence: float = Field(description="Confidence in extraction (0-1)")