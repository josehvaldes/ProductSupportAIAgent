"""
Chat API endpoints for the Shop Assistant.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from shopassist_api.application.ai_gen_deprecated.agents.shop_assistant import ShopAssistantAgent
from shopassist_api.domain.models.product import Product
from ..logging_config import get_logger
from datetime import datetime, timezone

logger = get_logger(__name__)

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    reply: str
    conversation_id: str
    created_time: Optional[str] = None
    suggestions: Optional[List[Product]] = None

@router.post("/dummy_chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Dummy chat endpoint for testing."""
    logger.info(f"Received dummy chat message: {request.message}")

    product:Product = { "id": f"test_1",
            "name": f"Test Product 1",
            "description": "A product for testing", 
            "category": "Testing", 
            "price": f"{14.5}", 
            "brand": "TestBrand", 
            "rating": "4.5", 
            "review_count": "10", 
            "product_url": f"http://example.com/product/test_1", 
            "image_url": f"https://m.media-amazon.com/images/I/41gikeSuhAL._SY300_SX300_QL70_FMwebp_.jpg",  
            "category_full": "Testing/Unit Tests", 
            "availability": "In Stock" }
    
    return ChatResponse(
        reply=f"Echo: {request.message}",
        conversation_id=request.conversation_id or "dummy_conversation",
        created_time= datetime.now(timezone.utc).isoformat(),
        suggestions=[
            product,
            Product(
                id="dummy2",
                name="Dummy Product 2",
                description="This is another dummy product.",
                category="Dummy Category",
                price=100.0,
                brand="Dummy Brand",
                image_url="https://m.media-amazon.com/images/I/31dJ+lXJq3L._SY300_SX300_.jpg",
                product_url="",
                rating=4.5, 
                review_count=155,
                category_full="category > subcategory",
                availability="In Stock"
            )
        ]
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the Shop Assistant AI.
    """
    try:
        # Initialize the shop assistant agent
        #
        agent = ShopAssistantAgent()
        
        # Process the user's message
        response = await agent.process_message(
            message=request.message,
            conversation_id=request.conversation_id,
            user_id=request.user_id
        )
        
        return ChatResponse(
            created_time= datetime.now(timezone.utc).isoformat(),
            reply=response.get("message", "I'm sorry, I couldn't process your request."),
            conversation_id=response.get("conversation_id", ""),
            suggestions=response.get("suggestions", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    """
    Get chat history for a conversation.
    """
    # TODO: Implement chat history retrieval
    return {"conversation_id": conversation_id, "messages": []}
