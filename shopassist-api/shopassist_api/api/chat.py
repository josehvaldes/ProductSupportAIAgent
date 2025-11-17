from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timezone

from shopassist_api.application.interfaces.di_container import get_session_manager, get_rag_service, get_repository_service
from shopassist_api.application.interfaces.service_interfaces import RepositoryServiceInterface
from shopassist_api.application.services.formaters import FormatterUtils
from shopassist_api.application.services.rag_service import RAGService
from shopassist_api.application.services.session_manager import SessionManager

from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    top_k: Optional[int] = 3

class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: List[Dict]
    query_type: str
    metadata: Dict

@router.post("/dumbmessage", response_model=ChatResponse)
async def chat_dump_message(request: ChatRequest,
                       rag_service:RAGService = Depends(get_rag_service)):
    """
    Process a chat message and return AI response
    """
    session_id = request.session_id or str(uuid.uuid4())
    user_id = "default_user"  # Placeholder for user identification
    # Get conversation history
    logger.info(f"Fetching conversation history for session_id: {session_id}, user_id: {user_id}, message: {request.message}")
    result = await rag_service.generate_dumb_answer(
        query=request.message,
        session_id=session_id
    )    

    return ChatResponse(
            session_id=session_id,
            response=result['response'],
            sources=result['sources'],
            query_type=result['query_type'],
            metadata=result['metadata']
        )


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest,
                       rag_service:RAGService = Depends(get_rag_service)):
    """
    Process a chat message and return AI response
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        user_id = "default_user"  # Placeholder for user identification
        # Get conversation history
        logger.info(f"Fetching conversation history for session_id: {session_id}, user_id: {user_id}, message: {request.message}")
        # Generate response using RAG
        result = await rag_service.generate_answer(
            user_id=user_id,
            query=request.message,
            session_id=session_id
        )

        return ChatResponse(
            session_id=session_id,
            response=result['response'],
            sources=result['sources'],
            query_type=result['query_type'],
            metadata = {
                "tokens": result['metadata'].get('tokens', {}),
                "cost": result['metadata'].get('cost', 0.0),
                "num_sources": result['metadata'].get('num_sources', 0),
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history_raw/{session_id}")
async def get_chat_history(session_id: str,
                           cosmos_service:RepositoryServiceInterface = Depends(get_repository_service)):
    """
    Get conversation history for a session
    """
    try:
        history = await cosmos_service.get_conversation_history(session_id)
        history_text = FormatterUtils.format_history(history)
        return {"session_id": session_id, "messages": history, "formatted_history": history_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
