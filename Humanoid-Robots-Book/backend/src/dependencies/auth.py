"""
Authentication Dependencies
Feature: 003-better-auth
Purpose: FastAPI dependencies for extracting current user from JWT

These dependencies are used in protected routes to:
1. Extract JWT token from Authorization header
2. Validate and decode the token
3. Return user information for the route handler
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from ..utils.jwt import decode_access_token

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Extract and validate current user from JWT token.

    This dependency:
    1. Extracts the Bearer token from Authorization header
    2. Decodes and validates the JWT
    3. Returns the full user profile from token claims

    **Usage in Protected Routes**:
    ```python
    @router.get("/protected")
    async def protected_route(user: dict = Depends(get_current_user)):
        return {"message": f"Hello {user['name']}!"}
    ```

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        dict: User profile with all claims from JWT

    Raises:
        HTTPException: 401 if token is invalid or expired

    **Token Format Expected**:
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_current_user_id(
    user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """
    Extract only the user ID from JWT token.

    Convenience dependency for routes that only need the user ID.

    **Usage**:
    ```python
    @router.get("/my-data")
    async def get_my_data(user_id: str = Depends(get_current_user_id)):
        # Query database using user_id
        return {"user_id": user_id}
    ```

    Args:
        user: User profile from get_current_user dependency

    Returns:
        str: User UUID from JWT 'user_id' claim

    Raises:
        HTTPException: 401 if token doesn't contain user_id
    """
    user_id = user.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )

    return user_id
