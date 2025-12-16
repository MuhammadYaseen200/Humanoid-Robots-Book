"""
Profile Router
Feature: 003-better-auth
Purpose: User profile management endpoints

Implements User Story 3 (Profile Management) for enhanced UX.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
import asyncpg
import logging

from ..models.profile import UserProfile, ProfileUpdateRequest, ProfileUpdateResponse
from ..dependencies.auth import get_current_user, get_current_user_id
from ..utils.jwt import create_access_token

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/profile",
    tags=["Profile"],
    responses={
        401: {"description": "Unauthorized"},
    },
)


# Database connection helper
async def get_db_connection() -> asyncpg.Connection:
    """Create database connection using asyncpg."""
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


@router.get(
    "/me",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Retrieve authenticated user's profile (stateless, from JWT claims)"
)
async def get_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> UserProfile:
    """
    User Story 3: Profile Management (Priority: P3)

    **Stateless Operation (ADR-006)**:
    - Profile data extracted directly from JWT claims
    - No database query required (SC-007)
    - JWT validation < 50ms

    **JWT Claims Structure**:
    - user_id (sub)
    - email
    - name
    - gpu_type
    - ram_capacity
    - coding_languages
    - robotics_experience

    **Returns**:
    - Complete user profile with all fields

    **Raises**:
    - 401 Unauthorized: Invalid or expired token
    """
    conn = await get_db_connection()

    try:
        user_id = current_user["sub"]

        # Fetch complete profile from database (includes fields not in JWT)
        profile_row = await conn.fetchrow(
            """
            SELECT
                u.id,
                u.email,
                u.name,
                u.created_at,
                u.last_login,
                p.gpu_type,
                p.ram_capacity,
                p.coding_languages,
                p.robotics_experience,
                p.learning_style,
                p.difficulty_level,
                p.preferred_language
            FROM users u
            JOIN user_profiles p ON u.id = p.user_id
            WHERE u.id = $1 AND u.is_active = true
            """,
            user_id
        )

        if not profile_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        # Parse JSONB coding_languages
        coding_languages_list = json.loads(profile_row['coding_languages'])

        # Build UserProfile response
        user_profile = UserProfile(
            id=str(profile_row['id']),
            email=profile_row['email'],
            name=profile_row['name'],
            gpu_type=profile_row['gpu_type'],
            ram_capacity=profile_row['ram_capacity'],
            coding_languages=coding_languages_list,
            robotics_experience=profile_row['robotics_experience'],
            learning_style=profile_row['learning_style'],
            difficulty_level=profile_row['difficulty_level'],
            preferred_language=profile_row['preferred_language'],
            created_at=profile_row['created_at'],
            last_login=profile_row['last_login']
        )

        return user_profile

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Get profile error for user {current_user.get('sub')}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve profile. Please try again later."
        )

    finally:
        await conn.close()


@router.put(
    "/me",
    response_model=ProfileUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user profile",
    description="Update hardware/software profile fields and get refreshed JWT token"
)
async def update_profile(
    profile_updates: ProfileUpdateRequest,
    user_id: str = Depends(get_current_user_id)
) -> ProfileUpdateResponse:
    """
    User Story 3: Profile Management - Update Profile (Priority: P3)

    Allows users to update their hardware/software profile:
    - GPU type (e.g., upgraded from integrated to RTX 4070 Ti)
    - RAM capacity (e.g., upgraded from 8GB to 32GB)
    - Coding languages (e.g., learned Rust and C++)
    - Robotics experience (e.g., completed course, now "Student")

    **Email cannot be changed** (FR-026) - permanent identifier.

    **JWT Token Refresh (FR-025)**:
    - Returns new JWT with updated profile claims
    - Frontend must replace old token with new one
    - Ensures personalization uses latest profile data

    **Returns**:
    - Updated user profile
    - Refreshed JWT token with new claims

    **Raises**:
    - 401 Unauthorized: Invalid or expired token
    - 422 Unprocessable Entity: Invalid profile field values
    - 500 Internal Server Error: Database failure
    """
    conn = await get_db_connection()

    try:
        # Build UPDATE query dynamically based on provided fields
        update_fields = []
        update_values = []
        param_index = 1

        # Only update fields that are provided (not None)
        if profile_updates.gpu_type is not None:
            update_fields.append(f"gpu_type = ${param_index}")
            update_values.append(profile_updates.gpu_type)
            param_index += 1

        if profile_updates.ram_capacity is not None:
            update_fields.append(f"ram_capacity = ${param_index}")
            update_values.append(profile_updates.ram_capacity)
            param_index += 1

        if profile_updates.coding_languages is not None:
            update_fields.append(f"coding_languages = ${param_index}::jsonb")
            update_values.append(json.dumps(profile_updates.coding_languages))
            param_index += 1

        if profile_updates.robotics_experience is not None:
            update_fields.append(f"robotics_experience = ${param_index}")
            update_values.append(profile_updates.robotics_experience)
            param_index += 1

        if profile_updates.learning_style is not None:
            update_fields.append(f"learning_style = ${param_index}")
            update_values.append(profile_updates.learning_style)
            param_index += 1

        if profile_updates.difficulty_level is not None:
            update_fields.append(f"difficulty_level = ${param_index}")
            update_values.append(profile_updates.difficulty_level)
            param_index += 1

        if profile_updates.preferred_language is not None:
            update_fields.append(f"preferred_language = ${param_index}")
            update_values.append(profile_updates.preferred_language)
            param_index += 1

        # If no fields to update, return current profile
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )

        # Add updated_at timestamp
        update_fields.append(f"updated_at = ${param_index}")
        update_values.append(datetime.utcnow())
        param_index += 1

        # Add user_id for WHERE clause
        update_values.append(user_id)

        # Execute update
        update_query = f"""
            UPDATE user_profiles
            SET {", ".join(update_fields)}
            WHERE user_id = ${param_index}
            RETURNING
                gpu_type,
                ram_capacity,
                coding_languages,
                robotics_experience,
                learning_style,
                difficulty_level,
                preferred_language
        """

        profile_row = await conn.fetchrow(update_query, *update_values)

        if not profile_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        # Fetch user data for JWT token generation
        user_row = await conn.fetchrow(
            "SELECT id, email, name, created_at, last_login FROM users WHERE id = $1",
            user_id
        )

        # Parse JSONB coding_languages
        coding_languages_list = json.loads(profile_row['coding_languages'])

        # Create refreshed JWT token with updated profile claims (FR-025)
        token = create_access_token(
            user_id=str(user_id),
            email=user_row['email'],
            name=user_row['name'],
            gpu_type=profile_row['gpu_type'],
            ram_capacity=profile_row['ram_capacity'],
            coding_languages=coding_languages_list,
            robotics_experience=profile_row['robotics_experience']
        )

        # Build updated UserProfile
        updated_profile = UserProfile(
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
            last_login=user_row['last_login']
        )

        logger.info(f"Profile updated for user {user_id}")

        return ProfileUpdateResponse(user=updated_profile, token=token)

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Update profile error for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update profile. Please try again later."
        )

    finally:
        await conn.close()
