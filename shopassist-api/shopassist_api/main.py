"""
FastAPI main application entry point for Shop Assistant API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shopassist_api.application.settings.config import settings
from shopassist_api.api import chat, health, products

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    debug=settings.debug,
)

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
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(products.router, prefix="/api/v1", tags=["products"])

def main():
    """Entry point for the CLI script."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
