from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, List, Dict, Optional
import uuid
from datetime import datetime, timezone

from shopassist_api.application.agents.orchestrator import AgentOrchestrator
from shopassist_api.application.interfaces.di_container import get_rag_service, get_repository_service
from shopassist_api.application.interfaces.service_interfaces import RepositoryServiceInterface
from shopassist_api.application.services.formaters import FormatterUtils
from shopassist_api.application.services.rag_service import RAGService

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
    sources: List[Any]
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

@router.post("/orchestrate", response_model=ChatResponse)
async def chat_orchestrator(request: ChatRequest):
    """
    Process a chat message using orchestrator and return AI response
    """

    orchestrator = AgentOrchestrator()
    session_id = request.session_id or str(uuid.uuid4().hex[:12])
    user_id = "default_user"  # Placeholder for user identification
    logger.info(f"Orchestrator processing for session_id: {session_id}, user_id: {user_id}, message: {request.message}")
    result = await orchestrator.ainvoke({
        "user_query": request.message,
        "session_Id": session_id
    })

    logger.info(f"Orchestrator response for session_id: {session_id} ready.")

    metadatas = result.get("metadatas", [])
    total_input_tokens = 0
    total_output_tokens = 0
    total_total_tokens = 0
    for metadata in metadatas:
        total_input_tokens += metadata.input_token or 0
        total_output_tokens += metadata.output_token or 0
        total_total_tokens += metadata.total_token or 0

    return ChatResponse(
        session_id=session_id,
        response=result['response'],
        sources=result['sources'],
        query_type=result['current_agent'],
        metadata = {
            "tokens": {
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "total_tokens": total_total_tokens
            },
            "cost": 0.0,
            "num_sources": len(result['sources']),
        }
    )



@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest,
                       rag_service:RAGService = Depends(get_rag_service)):
    """
    Process a chat message and return AI response
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4().hex[:12])
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
    
