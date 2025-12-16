"""
FastAPI Backend Entry Point - Authentication Feature
Feature: 003-better-auth
Purpose: Minimal FastAPI app with authentication and profile management

This is a simplified version of main.py focused on the authentication feature.
Once tested and working, this can be merged into the full main.py.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

from .routers import auth_router, profile_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Physical AI & Humanoid Robotics API - Auth Feature",
    description="Backend API with authentication and profile management (Feature 003-better-auth)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,  # Required for httpOnly cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ============================================================================
# Register Routers
# ============================================================================

# Authentication router (Signup, Signin, Signout)
app.include_router(auth_router)

# Profile router (GET/PUT /api/profile/me)
app.include_router(profile_router)


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Physical AI & Humanoid Robotics API - Auth Feature",
        "version": "1.0.0",
        "status": "operational",
        "features": ["authentication", "profile-management"],
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check for application status.

    For full health check including database connectivity,
    see the main.py implementation.
    """
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "authentication": "enabled",
            "profile_management": "enabled"
        }
    }


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    env = os.getenv("ENV", "development")

    # Run with auto-reload in development
    uvicorn.run(
        "backend.src.main_auth:app",
        host=host,
        port=port,
        reload=(env == "development"),
        log_level="info"
    )
