"""
FastAPI main application entry point for Shop Assistant API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shopassist_api.core.config import settings
from shopassist_api.api import chat, health

app = FastAPI(
    title="Shop Assistant API",
    description="AI-Powered Product Knowledge & Support Agent",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])

def main():
    """Entry point for the CLI script."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
