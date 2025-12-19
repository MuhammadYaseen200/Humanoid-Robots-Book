"""
JWT Token Utilities
Feature: 003-better-auth
Purpose: JWT token creation, validation, and management

Implements ADR-004 and ADR-006 decisions:
- JWT tokens with embedded profile claims for stateless personalization
- HS256 signing algorithm with AUTH_SECRET
- 24-hour expiration
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from jose import JWTError, jwt
import os

# JWT Configuration
AUTH_SECRET = os.getenv("AUTH_SECRET", "")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = int(os.getenv("JWT_EXPIRATION", "86400"))  # 24 hours default

# Validate AUTH_SECRET on module import
if not AUTH_SECRET or len(AUTH_SECRET) < 32:
    raise ValueError(
        "AUTH_SECRET environment variable must be set and at least 32 characters. "
        "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
    )


def create_access_token(
    user_id: str,
    email: str,
    name: str,
    gpu_type: str,
    ram_capacity: str,
    coding_languages: List[str],
    robotics_experience: str
) -> str:
    """
    Create JWT access token with embedded profile claims.

    **ADR-006 Decision**: Embed ALL profile fields in JWT for stateless personalization
    - Eliminates database lookup on /personalize requests (~100ms saved)
    - Token size ~500 bytes (well under 4KB cookie limit)
    - Profile changes reflected after JWT expires (max 24 hours staleness acceptable)

    Args:
        user_id: User UUID (JWT 'sub' claim)
        email: User email address
        name: User display name
        gpu_type: GPU hardware type
        ram_capacity: System RAM capacity
        coding_languages: List of programming languages
        robotics_experience: Robotics experience level

    Returns:
        str: Signed JWT token

    Example:
        >>> token = create_access_token(
        ...     user_id="550e8400-e29b-41d4-a716-446655440000",
        ...     email="user@example.com",
        ...     name="John Doe",
        ...     gpu_type="NVIDIA RTX 4070 Ti",
        ...     ram_capacity="16-32GB",
        ...     coding_languages=["Python", "C++"],
        ...     robotics_experience="Beginner (0-1 years)"
        ... )
        >>> assert len(token) > 100
        >>> decoded = decode_access_token(token)
        >>> assert decoded["user_id"] == "550e8400-e29b-41d4-a716-446655440000"
    """
    # Calculate expiration time
    expire = datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION_SECONDS)

    # Build JWT payload with profile claims
    payload = {
        # Standard JWT claims
        "sub": user_id,  # Subject (user ID)
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at

        # User profile claims for personalization
        "user_id": user_id,
        "email": email,
        "name": name,
        "gpu_type": gpu_type,
        "ram_capacity": ram_capacity,
        "coding_languages": coding_languages,
        "robotics_experience": robotics_experience,
    }

    # Sign and return token
    return jwt.encode(payload, AUTH_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT access token.

    **Security**:
    - Validates signature with AUTH_SECRET
    - Checks expiration time
    - Returns None on any validation failure

    Args:
        token: JWT token string

    Returns:
        dict: Decoded payload with user profile claims, or None if invalid

    Raises:
        No exceptions - returns None on validation failure for security

    Example:
        >>> token = create_access_token(...)
        >>> payload = decode_access_token(token)
        >>> assert payload is not None
        >>> assert "user_id" in payload
        >>> assert "gpu_type" in payload

        >>> invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid"
        >>> assert decode_access_token(invalid_token) is None
    """
    try:
        payload = jwt.decode(token, AUTH_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        # Invalid signature, expired, or malformed token
        return None
