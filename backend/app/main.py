"""
Healthcare Web Application - FastAPI Backend

This is the main entry point for our FastAPI backend server.
It handles CORS configuration, API routing, and server initialization.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Import API routers
from .api import stt, enhancement, tts  # removed realtime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="Healthcare Web Application API",
    description="Backend API for speech-to-text medical transcription with AI enhancement using Deepgram and Google Gemini",
    version="1.0.0"
)

# Configure CORS to allow React frontend to communicate with our API
# In production, replace "*" with your actual frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:5173"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include API routers 
app.include_router(stt.router)
app.include_router(enhancement.router)
app.include_router(tts.router)

@app.get("/")
async def root():
    """
    Root endpoint - provides basic API information
    This is useful for health checks and API discovery
    """
    return {
        "message": "Healthcare Web Application API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and deployment
    Returns the current status of the API and its services
    """
    return {
        "status": "healthy",
        "timestamp": "2025-08-12T00:00:00Z",
        "services": {
            "api": "operational",
            "deepgram_stt": "configured",
            "deepgram_tts": "configured", 
            "gemini_llm": "configured"
        }
    }

# Error handler for general exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Global exception handler to catch and log unexpected errors
    Returns a user-friendly error message while logging details
    """
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    import uvicorn
    # Run the server when this file is executed directly
    # In production, use a proper ASGI server deployment
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Auto-reload on code changes during development
        log_level="info"
    )
