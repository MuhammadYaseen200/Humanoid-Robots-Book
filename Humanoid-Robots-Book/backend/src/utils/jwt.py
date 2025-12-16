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
        gpu_type: User GPU hardware type
        ram_capacity: User system RAM capacity
        coding_languages: List of programming languages user knows
        robotics_experience: User robotics background level

    Returns:
        Signed JWT token string

    Raises:
        ValueError: If AUTH_SECRET not configured

    Example:
        >>> token = create_access_token(
        ...     user_id="550e8400-e29b-41d4-a716-446655440000",
        ...     email="student@example.com",
        ...     name="John Doe",
        ...     gpu_type="NVIDIA RTX 4070 Ti",
        ...     ram_capacity="16-32GB",
        ...     coding_languages=["Python", "C++"],
        ...     robotics_experience="Hobbyist (built simple projects)"
        ... )
        >>> print(len(token))  # ~500 bytes
        500

    Reference:
        - ADR-006: Hardware Profile Data Management (JWT claims strategy)
        - data-model.md lines 155-206: JWT claims structure
    """
    # Calculate expiration timestamp
    now = datetime.utcnow()
    expires_at = now + timedelta(seconds=JWT_EXPIRATION_SECONDS)

    # Build JWT payload with standard + custom claims
    payload: Dict[str, Any] = {
        # Standard JWT claims (RFC 7519)
        "sub": user_id,  # Subject: user UUID
        "iat": int(now.timestamp()),  # Issued At: Unix timestamp
        "exp": int(expires_at.timestamp()),  # Expiration: Unix timestamp

        # Custom claims: User identity
        "email": email,
        "name": name,

        # Custom claims: Hardware profile for personalization (THE 50-POINT FEATURE)
        "gpu_type": gpu_type,
        "ram_capacity": ram_capacity,
        "coding_languages": coding_languages,
        "robotics_experience": robotics_experience
    }

    # Sign and encode JWT
    token = jwt.encode(payload, AUTH_SECRET, algorithm=JWT_ALGORITHM)

    return token


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.

    Validates:
    - Signature (using AUTH_SECRET)
    - Expiration (exp claim)
    - Token format

    Args:
        token: JWT token string

    Returns:
        Decoded JWT payload (dictionary with all claims)

    Raises:
        JWTError: If token is invalid, expired, or signature mismatch

    Example:
        >>> payload = decode_token(token)
        >>> print(payload["sub"])  # User ID
        550e8400-e29b-41d4-a716-446655440000
        >>> print(payload["gpu_type"])  # Profile claim
        NVIDIA RTX 4070 Ti

    Reference:
        - Used by JWT authentication dependency (T015)
        - Enables stateless authentication (no database lookup)
    """
    try:
        # Decode and validate JWT
        # This validates signature and expiration automatically
        payload = jwt.decode(token, AUTH_SECRET, algorithms=[JWT_ALGORITHM])
        return payload

    except JWTError as e:
        # Token invalid, expired, or signature mismatch
        raise JWTError(f"Invalid or expired token: {str(e)}")


def create_reset_token(email: str, reset_counter: int) -> str:
    """
    Create password reset JWT token with short expiration.

    **Security (ADR-005)**:
    - 1-hour expiration (short-lived)
    - Includes reset_counter to invalidate previous tokens
    - Separate token type to prevent confusion with access tokens

    Args:
        email: User email address
        reset_counter: Current reset counter from database (incremented on each reset)

    Returns:
        Signed JWT reset token

    Example:
        >>> reset_token = create_reset_token("user@example.com", reset_counter=5)
        >>> # Send reset link: https://example.com/reset-password?token={reset_token}

    Reference:
        - data-model.md lines 208-245: Password reset token structure
        - Used by POST /api/auth/forgot-password (T036)
    """
    now = datetime.utcnow()
    expires_at = now + timedelta(hours=1)  # 1-hour expiration

    payload: Dict[str, Any] = {
        "sub": email,
        "type": "password_reset",
        "reset_counter": reset_counter,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp())
    }

    token = jwt.encode(payload, AUTH_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_reset_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate password reset token.

    Additional validation:
    - Checks token type is "password_reset"
    - Returns email and reset_counter for validation

    Args:
        token: JWT reset token string

    Returns:
        Decoded payload with email and reset_counter

    Raises:
        JWTError: If token invalid, expired, or wrong type
        ValueError: If token type is not "password_reset"

    Example:
        >>> payload = decode_reset_token(reset_token)
        >>> email = payload["sub"]
        >>> reset_counter = payload["reset_counter"]
        >>> # Validate reset_counter matches database value

    Reference:
        - Used by POST /api/auth/reset-password (T037)
    """
    try:
        payload = jwt.decode(token, AUTH_SECRET, algorithms=[JWT_ALGORITHM])

        # Validate token type
        if payload.get("type") != "password_reset":
            raise ValueError("Invalid token type (expected password_reset)")

        return payload

    except JWTError as e:
        raise JWTError(f"Invalid or expired reset token: {str(e)}")


def extract_user_id_from_token(token: str) -> str:
    """
    Extract user ID from JWT token without full validation.

    **Use Case**: Quick user ID extraction for logging/analytics
    **Warning**: Does NOT validate signature or expiration - use decode_token() for security

    Args:
        token: JWT token string

    Returns:
        User ID (sub claim)

    Example:
        >>> user_id = extract_user_id_from_token(token)
        >>> logger.info(f"Request from user {user_id}")
    """
    try:
        # Decode without verification (faster, but insecure)
        unverified = jwt.get_unverified_claims(token)
        return unverified.get("sub", "")
    except:
        return ""


def is_token_expired(token: str) -> bool:
    """
    Check if JWT token is expired without raising exception.

    Args:
        token: JWT token string

    Returns:
        True if expired, False if still valid

    Example:
        >>> if is_token_expired(token):
        ...     print("Token expired, please sign in again")
    """
    try:
        payload = jwt.get_unverified_claims(token)
        exp = payload.get("exp", 0)
        now = datetime.utcnow().timestamp()
        return now >= exp
    except:
        return True  # Treat invalid tokens as expired


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get expiration datetime from JWT token.

    Args:
        token: JWT token string

    Returns:
        Expiration datetime, or None if invalid

    Example:
        >>> exp_time = get_token_expiration(token)
        >>> print(f"Token expires at {exp_time}")
        Token expires at 2025-12-17 14:30:00
    """
    try:
        payload = jwt.get_unverified_claims(token)
        exp = payload.get("exp")
        if exp:
            return datetime.fromtimestamp(exp)
        return None
    except:
        return None
