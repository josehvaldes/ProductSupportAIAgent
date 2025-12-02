"""
FastAPI main application entry point for Shop Assistant API.
"""
import os
from dotenv import load_dotenv 
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from shopassist_api.application.settings.config import settings
from shopassist_api.api import chat, health, products, search, session
from shopassist_api.logging_config import setup_logging
from .logging_config import get_logger
from contextlib import asynccontextmanager
import time
from shopassist_api.application.interfaces.di_container import (
    get_category_embedding_service,
    get_embedding_service,
    get_llm_service,
    get_vector_service
)

load_dotenv()

setup_logging(
        log_level=settings.log_level,
        log_file=settings.log_file,
        log_to_console=settings.log_to_console
    )

logger = get_logger(__name__)

async def warmup_services():
    """Preload and warmup singleton services."""
    logger.info(f"Warming up services... {settings.embedding_provider} embedding service")
    
    # Embedding Service
    try:
        embedding_service = get_embedding_service()
        if hasattr(embedding_service, 'generate_embedding'):
            # Generate a dummy embedding to load the model into memory
            logger.info("Warming up embedding service model...")
            await embedding_service.generate_embedding("initialization warmup")
        
        category_embedding = get_category_embedding_service()
        if hasattr(category_embedding, 'generate_embedding'):
            logger.info("Warming up category embedding service model...")
            # Generate a dummy embedding to load the model into memory
            await category_embedding.generate_embedding("initialization warmup")
        
        logger.info("✓ Embedding services ready")

    except Exception as e:
        logger.error(f"Failed to initialize embedding service: {e}")
    
    # LLM Service
    try:
        llm_service = get_llm_service()
        logger.info("✓ LLM service ready")
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {e}")
    
    # Vector Service
    try:
        vector_service = get_vector_service()
        # Optional: test connection
        # await vector_service.health_check()
        logger.info("✓ Vector service ready")
    except Exception as e:
        logger.error(f"Failed to initialize vector service: {e}")
    
    logger.info("Service warmup complete!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting ShopAssist API...")
    logger.info(f"API Title: {settings.api_title} Version: {settings.api_version}")
    
    # Warmup services
    await warmup_services()
    
    yield
    
    # Shutdown
    logger.info("Shutting down ShopAssist API...")


app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan
)


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.warning(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Duration: {process_time:.3f}s"
    )
    return response

# CORS settings
origins = ["http://localhost:5173", 
           "http://localhost:8080",
           "http://shopassist-api:8080" # internal access from shopassist-ui container
           ]  # React dev servers

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(session.router, prefix="/api/v1/session", tags=["search"])

def run_production():
    """Entry point for the CLI script."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_production()
