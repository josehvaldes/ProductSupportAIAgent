"""
Health check endpoint.
"""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from shopassist_api.application.interfaces.di_container import get_cache_service, get_rag_service, get_repository_service
from shopassist_api.application.interfaces.service_interfaces import CacheServiceInterface, RepositoryServiceInterface
from shopassist_api.application.services.rag_service import RAGService
from shopassist_api.application.settings.config import settings
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/")
async def health_check(cosmos_service:RepositoryServiceInterface = Depends(get_repository_service),
                       rag_service:RAGService = Depends(get_rag_service),
                       cache_service:CacheServiceInterface = Depends(get_cache_service)):
    """Health check endpoint."""
    all_healthy = True
    repo_check ={}
    try:
        is_healthy = await cosmos_service.health_check()
        repo_check['repository_service'] = "healthy" if is_healthy else "unhealthy"
        all_healthy = all_healthy and is_healthy
    except Exception as e:
        repo_check['repository_service'] = f"unhealthy: {str(e)}"

    rag_check ={}
    try:
        rag_check = await rag_service.health_check()
        is_healthy = rag_check["is_healthy"]
        all_healthy = all_healthy and is_healthy
    except Exception as e:
        rag_check['rag_service'] = f"unhealthy: {str(e)}"

    cache_check = {}
    try:
        is_healthy = await cache_service.health_check()
        cache_check['cache_service'] = "healthy" if is_healthy else "unhealthy"
        all_healthy = all_healthy and is_healthy
    except Exception as e:
        cache_check['cache_service'] = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "timestamp": datetime.now(timezone.utc),
        "service": settings.api_title,
        "version": settings.api_version,
        **repo_check,
        **cache_check,
        "rag_service": rag_check,
    }
