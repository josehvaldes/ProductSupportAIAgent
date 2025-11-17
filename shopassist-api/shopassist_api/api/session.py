from fastapi import APIRouter, Depends, HTTPException

from shopassist_api.application.interfaces.di_container import get_session_manager, get_rag_service, get_repository_service
from shopassist_api.application.services.session_manager import SessionManager

from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/start")
async def start_session(
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Create new chat session"""
    user_id = "default_user"  # Placeholder for user identification
    session_id = await session_manager.create_session(user_id)
    return {"session_id": session_id}

@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get conversation history"""
    history = await session_manager.get_conversation_history(session_id)
    return {"messages": history}

@router.delete("/{session_id}")
async def clear_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Clear session (new conversation)"""
    user_id = "default_user"  # Placeholder for user identification
    await session_manager.delete_session(user_id, session_id)
    return {"status": "cleared"}

@router.get("/preferences/{session_id}")
async def get_preferences(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get extracted user preferences"""
    prefs = await session_manager.get_preferences(session_id)
    if prefs is None:
        return { "preferences.": {} }
    return prefs.model_dump( mode="json" )