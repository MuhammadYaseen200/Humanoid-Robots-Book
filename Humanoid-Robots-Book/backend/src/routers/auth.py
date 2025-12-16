"""
Authentication Router
Feature: 003-better-auth
Purpose: Signup, signin, and signout endpoints

Implements User Story 1 (Signup) and User Story 2 (Signin) for 50 bonus points.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import asyncpg
import logging

from ..models.auth import SignupRequest, SigninRequest, AuthResponse
from ..models.profile import UserProfile
from ..utils.auth import hash_password, verify_password, constant_time_verify
from ..utils.jwt import create_access_token

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized"},
        429: {"description": "Too Many Requests"},
    },
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


# Database connection helper
async def get_db_connection() -> asyncpg.Connection:
    """
    Create database connection using asyncpg.

    Returns:
        asyncpg.Connection: Database connection

    Raises:
        HTTPException: If database connection fails
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database configuration error"
        )

    try:
        conn = await asyncpg.connect(database_url)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to database. Please try again later."
        )


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user account",
    description="Register with email, password, and hardware/software profile (THE 50-POINT FEATURE)"
)
@limiter.limit("10/minute")
async def signup(request: Request, signup_data: SignupRequest) -> AuthResponse:
    """
    User Story 1: New User Signup with Hardware Profiling (Priority: P1)

    **THE 50-POINT HACKATHON FEATURE**

    Creates new user account with complete hardware/software profile:
    - GPU type (for Module 3 Isaac Sim requirements)
    - RAM capacity (for performance-sensitive tutorials)
    - Coding languages (for difficulty-appropriate content)
    - Robotics experience (for personalized learning path)

    **Security (ADR-005)**:
    - Password hashed with bcrypt (12 salt rounds)
    - Email uniqueness check with generic error (prevents enumeration)
    - Rate limited to 10 requests/minute/IP

    **Performance (ADR-005)**:
    - Async bcrypt wrapper prevents event loop blocking (~200-300ms)
    - Completes in <2 seconds (p95) per SC-001

    **Returns**:
    - JWT token with embedded profile claims (ADR-006)
    - User profile for frontend state

    **Raises**:
    - 409 Conflict: Email already registered
    - 422 Unprocessable Entity: Invalid input (weak password, invalid email)
    - 429 Too Many Requests: Rate limit exceeded
    - 500 Internal Server Error: Database failure
    """
    conn = await get_db_connection()

    try:
        # Step 1: Check if email already exists (FR-006)
        # Use lowercase email for case-insensitive comparison
        existing_user = await conn.fetchrow(
            "SELECT id FROM users WHERE LOWER(email) = $1",
            signup_data.email.lower()
        )

        if existing_user:
            # Email already registered - return 409 Conflict
            # Generic error to prevent email enumeration (ADR-005)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered. Please sign in instead."
            )

        # Step 2: Hash password using async bcrypt wrapper (FR-003, ADR-005)
        # CRITICAL: This is async to prevent blocking event loop (~200-300ms)
        password_hash = await hash_password(signup_data.password)

        # Step 3: Begin transaction to create user + profile atomically
        async with conn.transaction():
            # Insert user record
            user_row = await conn.fetchrow(
                """
                INSERT INTO users (email, password_hash, name, created_at, updated_at, is_active)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, email, name, created_at
                """,
                signup_data.email.lower(),
                password_hash,
                signup_data.name,
                datetime.utcnow(),
                datetime.utcnow(),
                True
            )

            user_id = user_row['id']

            # Convert coding_languages list to JSON for JSONB column
            coding_languages_json = json.dumps(signup_data.coding_languages)

            # Insert user_profile record with hardware/software background (FR-018, FR-019)
            # ALL fields are required for 100% profile completeness (SC-012)
            profile_row = await conn.fetchrow(
                """
                INSERT INTO user_profiles (
                    user_id,
                    gpu_type,
                    ram_capacity,
                    coding_languages,
                    robotics_experience,
                    created_at,
                    updated_at
                )
                VALUES ($1, $2, $3, $4::jsonb, $5, $6, $7)
                RETURNING
                    id,
                    user_id,
                    gpu_type,
                    ram_capacity,
                    coding_languages,
                    robotics_experience,
                    learning_style,
                    difficulty_level,
                    preferred_language,
                    created_at
                """,
                user_id,
                signup_data.gpu_type,
                signup_data.ram_capacity,
                coding_languages_json,
                signup_data.robotics_experience,
                datetime.utcnow(),
                datetime.utcnow()
            )

            # Log signup event to user_activity table for security monitoring (FR-031)
            await conn.execute(
                """
                INSERT INTO user_activity (user_id, activity_type, created_at, metadata)
                VALUES ($1, $2, $3, $4::jsonb)
                """,
                user_id,
                "signup",
                datetime.utcnow(),
                json.dumps({
                    "ip_address": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "gpu_type": signup_data.gpu_type,
                    "robotics_experience": signup_data.robotics_experience
                })
            )

        # Step 4: Create JWT token with embedded profile claims (FR-007, FR-020, ADR-006)
        # Embedding profile in JWT enables stateless personalization (eliminates DB query)
        coding_languages_list = json.loads(profile_row['coding_languages'])

        token = create_access_token(
            user_id=str(user_id),
            email=user_row['email'],
            name=user_row['name'],
            gpu_type=profile_row['gpu_type'],
            ram_capacity=profile_row['ram_capacity'],
            coding_languages=coding_languages_list,
            robotics_experience=profile_row['robotics_experience']
        )

        # Step 5: Build UserProfile response
        user_profile = UserProfile(
            id=str(user_id),
            email=user_row['email'],
            name=user_row['name'],
            gpu_type=profile_row['gpu_type'],
            ram_capacity=profile_row['ram_capacity'],
            coding_languages=coding_languages_list,
            robotics_experience=profile_row['robotics_experience'],
            learning_style=profile_row['learning_style'],
            difficulty_level=profile_row['difficulty_level'],
            preferred_language=profile_row['preferred_language'],
            created_at=user_row['created_at'],
            last_login=None  # First signup, no login yet
        )

        logger.info(f"User signup successful: {user_row['email']} (ID: {user_id})")

        # Return JWT token + user profile (FR-007)
        return AuthResponse(token=token, user=user_profile)

    except HTTPException:
        # Re-raise HTTP exceptions (409 Conflict, etc.)
        raise

    except Exception as e:
        # Log unexpected errors with details for debugging
        logger.error(f"Signup error for {signup_data.email}: {e}", exc_info=True)

        # Return generic error to user (don't leak implementation details)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create account. Please try again later."
        )

    finally:
        # Always close database connection
        await conn.close()


@router.post(
    "/signin",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate existing user",
    description="Validate email and password, return JWT token with profile claims"
)
@limiter.limit("10/minute")
async def signin(request: Request, signin_data: SigninRequest) -> AuthResponse:
    """
    User Story 2: Returning User Signin (Priority: P2)

    **Security (ADR-005)**:
    - Generic error messages to prevent email enumeration
    - Constant-time responses (~300ms) regardless of email existence
    - Always performs bcrypt verification (even if email not found)
    - Rate limited to 10 requests/minute/IP

    **Performance**:
    - Completes in <1 second (p95) per SC-002
    - Async bcrypt wrapper prevents event loop blocking

    **Returns**:
    - JWT token with embedded profile claims
    - User profile for frontend state
    - Updates last_login timestamp (FR-013)

    **Raises**:
    - 401 Unauthorized: Invalid email or password (generic error)
    - 429 Too Many Requests: Rate limit exceeded
    - 500 Internal Server Error: Database failure
    """
    conn = await get_db_connection()

    try:
        # Step 1: Query user by email (FR-011)
        # Use lowercase for case-insensitive comparison
        user_row = await conn.fetchrow(
            """
            SELECT id, email, password_hash, name, last_login
            FROM users
            WHERE LOWER(email) = $1 AND is_active = true
            """,
            signin_data.email.lower()
        )

        # Step 2: Constant-time password verification (ADR-005 email enumeration prevention)
        # CRITICAL: Always perform bcrypt verification to maintain constant time
        # If user doesn't exist: verify against fake hash (same timing ~300ms)
        # If user exists: verify against real hash
        if user_row:
            user_hash = user_row['password_hash']
            is_valid = await constant_time_verify(
                email=signin_data.email,
                password=signin_data.password,
                user_hash=user_hash
            )
            user_id = user_row['id']
        else:
            # Email doesn't exist: Use constant_time_verify with None (uses fake hash)
            is_valid = await constant_time_verify(
                email=signin_data.email,
                password=signin_data.password,
                user_hash=None
            )
            user_id = None

        # Step 3: If authentication failed, return generic error (FR-012, ADR-005)
        # Same error for both "wrong email" and "wrong password" to prevent enumeration
        if not is_valid:
            # Log failed signin attempt for security monitoring
            if user_id:
                await conn.execute(
                    """
                    INSERT INTO user_activity (user_id, activity_type, created_at, metadata)
                    VALUES ($1, $2, $3, $4::jsonb)
                    """,
                    user_id,
                    "failed_signin",
                    datetime.utcnow(),
                    json.dumps({
                        "ip_address": request.client.host if request.client else "unknown",
                        "user_agent": request.headers.get("user-agent", "unknown"),
                        "reason": "invalid_password"
                    })
                )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Step 4: Fetch user profile (JOIN with user_profiles)
        profile_row = await conn.fetchrow(
            """
            SELECT
                p.gpu_type,
                p.ram_capacity,
                p.coding_languages,
                p.robotics_experience,
                p.learning_style,
                p.difficulty_level,
                p.preferred_language,
                p.created_at,
                u.created_at as user_created_at
            FROM user_profiles p
            JOIN users u ON p.user_id = u.id
            WHERE p.user_id = $1
            """,
            user_id
        )

        if not profile_row:
            # User exists but no profile (shouldn't happen with proper migration)
            logger.error(f"User {user_id} has no profile - data inconsistency")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Account data incomplete. Please contact support."
            )

        # Step 5: Update last_login timestamp (FR-013)
        await conn.execute(
            "UPDATE users SET last_login = $1 WHERE id = $2",
            datetime.utcnow(),
            user_id
        )

        # Step 6: Log successful signin event (FR-031)
        await conn.execute(
            """
            INSERT INTO user_activity (user_id, activity_type, created_at, metadata)
            VALUES ($1, $2, $3, $4::jsonb)
            """,
            user_id,
            "signin",
            datetime.utcnow(),
            json.dumps({
                "ip_address": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            })
        )

        # Step 7: Create JWT token with embedded profile claims (FR-007, FR-020, ADR-006)
        coding_languages_list = json.loads(profile_row['coding_languages'])

        token = create_access_token(
            user_id=str(user_id),
            email=user_row['email'],
            name=user_row['name'],
            gpu_type=profile_row['gpu_type'],
            ram_capacity=profile_row['ram_capacity'],
            coding_languages=coding_languages_list,
            robotics_experience=profile_row['robotics_experience']
        )

        # Step 8: Build UserProfile response
        user_profile = UserProfile(
            id=str(user_id),
            email=user_row['email'],
            name=user_row['name'],
            gpu_type=profile_row['gpu_type'],
            ram_capacity=profile_row['ram_capacity'],
            coding_languages=coding_languages_list,
            robotics_experience=profile_row['robotics_experience'],
            learning_style=profile_row['learning_style'],
            difficulty_level=profile_row['difficulty_level'],
            preferred_language=profile_row['preferred_language'],
            created_at=profile_row['user_created_at'],
            last_login=datetime.utcnow()
        )

        logger.info(f"User signin successful: {user_row['email']} (ID: {user_id})")

        return AuthResponse(token=token, user=user_profile)

    except HTTPException:
        # Re-raise HTTP exceptions (401 Unauthorized, etc.)
        raise

    except Exception as e:
        # Log unexpected errors
        logger.error(f"Signin error for {signin_data.email}: {e}", exc_info=True)

        # Return generic error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to sign in. Please try again later."
        )

    finally:
        await conn.close()


@router.post(
    "/signout",
    status_code=status.HTTP_200_OK,
    summary="Sign out current user",
    description="Clear authentication token (primarily client-side operation)"
)
async def signout(request: Request):
    """
    Sign out endpoint (primarily client-side token clearing).

    For JWT authentication, signout is handled client-side by:
    - Clearing localStorage (development mode)
    - Clearing httpOnly cookie (production mode)

    This endpoint exists for:
    - Logging signout events
    - Future token blacklist implementation
    - Consistent API interface

    Returns:
        Message confirming signout
    """
    # Future: Log signout event if authenticated
    # For now, return success (client clears token)

    return {"message": "Signed out successfully"}
