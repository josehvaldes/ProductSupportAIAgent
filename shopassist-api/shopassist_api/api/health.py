"""
Health check endpoint.
"""
from fastapi import APIRouter
#import datetime
from datetime import datetime, timezone
from shopassist_api.application.settings.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc),
        "service": settings.api_title,
        "version": settings.api_version,
        "database": f"connected to {settings.database_url}" if settings.database_url else "not configured"
    }
