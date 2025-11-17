"""
FastAPI main application entry point for Shop Assistant API.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from shopassist_api.application.settings.config import settings
from shopassist_api.api import chat, health, products, search, session
from shopassist_api.logging_config import setup_logging
from .logging_config import get_logger
from contextlib import asynccontextmanager
import time

setup_logging(
        log_level=settings.log_level,
        log_file=settings.log_file,
        log_to_console=settings.log_to_console
    )

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    
    logger.info("Starting ShopAssist API...")
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
origins = ["http://localhost:5173"]  # React dev server

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
