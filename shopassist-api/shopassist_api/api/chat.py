from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timezone

from shopassist_api.application.interfaces.di_container import get_rag_service, get_repository_service
from shopassist_api.application.interfaces.service_interfaces import RepositoryServiceInterface
from shopassist_api.application.services.rag_service import RAGService

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: List[Dict]
    query_type: str
    metadata: Dict



@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest,
                       cosmos_service:RepositoryServiceInterface = Depends(get_repository_service),
                       rag_service:RAGService = Depends(get_rag_service)):
    """
    Process a chat message and return AI response
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        user_id = "default_user"  # Placeholder for user identification
        # Get conversation history
        history = await cosmos_service.get_conversation_history(session_id)
        
        # Generate response using RAG
        result = await rag_service.generate_answer(
            query=request.message,
            conversation_history=history,
            session_id=session_id
        )
        
        # Save conversation
        _ = await cosmos_service.save_message(
            session_id=session_id,
            user_id=user_id,
            role="user",
            content=request.message,
            timestamp=datetime.now(timezone.utc)
        )
        
        _ = await cosmos_service.save_message(
            session_id=session_id,
            role="assistant",
            user_id=user_id,
            content=result['response'],
            timestamp=datetime.now(timezone.utc),
            metadata=result['metadata']
        )
        
        return ChatResponse(
            session_id=session_id,
            response=result['response'],
            sources=result['sources'],
            query_type=result['query_type'],
            metadata=result['metadata']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str,
                           cosmos_service:RepositoryServiceInterface = Depends(get_repository_service)):
    """
    Get conversation history for a session
    """
    try:
        history = await cosmos_service.get_conversation_history(session_id)
        return {"session_id": session_id, "messages": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))