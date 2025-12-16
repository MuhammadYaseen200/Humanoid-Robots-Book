"""
Authentication Dependencies
Feature: 003-better-auth
Purpose: FastAPI dependencies for JWT authentication and authorization

Usage:
    @app.get("/api/profile")
    async def get_profile(current_user: dict = Depends(get_current_user)):
        return current_user
"""

from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from ..utils.jwt import decode_token

# HTTPBearer security scheme for extracting Bearer tokens from Authorization header
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency for JWT authentication.

    Extracts and validates JWT token from:
    1. Authorization header: "Bearer <token>"
    2. (Future) httpOnly cookie: "auth_token"

    Returns decoded JWT payload with user profile claims:
    - sub (user_id)
    - email
    - name
    - gpu_type
    - ram_capacity
    - coding_languages
    - robotics_experience

    Raises:
        HTTPException 401: If token missing, invalid, or expired

    Example:
        >>> @app.get("/api/profile")
        >>> async def get_profile(current_user: dict = Depends(get_current_user)):
        ...     user_id = current_user["sub"]
        ...     email = current_user["email"]
        ...     gpu_type = current_user["gpu_type"]
        ...     return {"user_id": user_id, "gpu": gpu_type}

    Reference:
        - ADR-006: JWT claims contain embedded profile for stateless authentication
        - Tasks T015: JWT authentication dependency
    """
    # Check if credentials provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token
    token = credentials.credentials

    try:
        # Decode and validate JWT
        # This validates signature and expiration automatically
        payload = decode_token(token)

        # Ensure required claims are present
        if "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError as e:
        # Token invalid, expired, or signature mismatch
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """
    Convenience dependency to extract only user ID from JWT.

    Example:
        >>> @app.put("/api/profile")
        >>> async def update_profile(
        ...     user_id: str = Depends(get_current_user_id),
        ...     updates: ProfileUpdateRequest
        ... ):
        ...     # Update user_profiles WHERE user_id = user_id
        ...     pass

    Reference:
        - Simpler than extracting from full current_user dict
        - Use when only user ID needed (not full profile)
    """
    return current_user["sub"]


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Optional authentication dependency.

    Returns user profile if authenticated, None if not authenticated.
    Does NOT raise exception for missing/invalid tokens.

    Use Case:
        - Endpoints that provide enhanced features for authenticated users
        - But also work for anonymous users

    Example:
        >>> @app.get("/api/chapters/{chapter_id}")
        >>> async def get_chapter(
        ...     chapter_id: int,
        ...     user: Optional[dict] = Depends(get_optional_user)
        ... ):
        ...     # If user authenticated: include progress, bookmarks
        ...     # If anonymous: return public content only
        ...     is_authenticated = user is not None
        ...     return {"chapter": chapter_id, "authenticated": is_authenticated}

    Reference:
        - Useful for hybrid public/private content
        - Gracefully degrades when token missing
    """
    if not credentials:
        return None

    token = credentials.credentials

    try:
        payload = decode_token(token)
        return payload if "sub" in payload else None
    except JWTError:
        # Token invalid/expired - treat as anonymous
        return None


# Future: Cookie-based authentication dependency (ADR-004 production mode)
async def get_current_user_from_cookie(
    # request: Request  # Uncomment when implementing cookie support
) -> Dict[str, Any]:
    """
    Extract JWT from httpOnly cookie (production mode).

    **NOT YET IMPLEMENTED** - Placeholder for ADR-004 production strategy.

    When implemented:
    1. Extract 'auth_token' cookie from request
    2. Decode and validate JWT
    3. Return user payload

    Reference:
        - ADR-004: httpOnly cookies for production (XSS protection)
        - Task T042: Implement httpOnly cookie support
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Cookie authentication not yet implemented. Use Authorization header.",
    )
