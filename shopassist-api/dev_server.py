#!/usr/bin/env python3
"""
Development server startup script.
"""
import uvicorn

from shopassist_api.application.settings.config import settings

def main():
    """Development server entry point."""
    print(f"Starting ShopAssist API Development Server.")
    uvicorn.run(
        "shopassist_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
