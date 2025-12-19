"""
User Profile Router
Feature: 003-better-auth
Purpose: Get and update user profile endpoints

**Endpoints**:
- GET /me: Retrieve current user's profile
- PUT /me: Update user's profile and hardware settings
"""

from fastapi import APIRouter, HTTPException, status, Depends
import asyncpg
import os
import logging
import json

from ..models.profile import UserProfile, ProfileUpdateRequest, ProfileUpdateResponse
from ..utils.jwt import create_access_token
from ..dependencies.auth import get_current_user, get_current_user_id

# Setup
router = APIRouter(prefix="/profile", tags=["User Profile"])
logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL")


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get Current User Profile",
    description="""
    Retrieve the authenticated user's profile with hardware settings.

    **Performance**: Profile data is embedded in JWT (ADR-006), so this
    endpoint simply returns the claims from the token without a database query.

    **Requires**: Valid JWT token in Authorization header
    """
)
async def get_my_profile(user: dict = Depends(get_current_user)):
    """
    Get current user profile from JWT claims.

    **ADR-006 Optimization**: Profile data is embedded in JWT, eliminating
    the need for a database query. This saves ~100ms per request.

    **Returns**: User profile with all hardware settings
    """
    return UserProfile(
        id=user["user_id"],
        email=user["email"],
        name=user["name"],
        gpu_type=user["gpu_type"],
        ram_capacity=user["ram_capacity"],
        coding_languages=user["coding_languages"],
        robotics_experience=user["robotics_experience"]
    )


@router.put(
    "/me",
    response_model=ProfileUpdateResponse,
    summary="Update Current User Profile",
    description="""
    Update the authenticated user's profile and hardware settings.

    **Features**:
    - Partial updates (only provided fields are updated)
    - Returns new JWT token with updated profile claims
    - Updates both users table (name) and user_profiles table (hardware)

    **Token Refresh**: Since profile claims are embedded in JWT (ADR-006),
    a new token is issued with updated claims. Client must replace the old token.

    **Requires**: Valid JWT token in Authorization header
    """
)
async def update_my_profile(
    update_data: ProfileUpdateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Update user profile and return new JWT with updated claims.

    **Flow**:
    1. Validate at least one field is provided
    2. Update users table if name changed
    3. Update user_profiles table if hardware settings changed
    4. Fetch complete updated profile
    5. Generate new JWT with updated claims
    6. Return new token + updated profile

    **ADR-006 Implication**: Profile changes require token refresh since
    claims are embedded in JWT. Max staleness = JWT expiration (24 hours).
    """
    try:
        # Validate at least one field is provided
        if not any([
            update_data.name,
            update_data.gpu_type,
            update_data.ram_capacity,
            update_data.coding_languages,
            update_data.robotics_experience
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field must be provided for update"
            )

        conn = await asyncpg.connect(DATABASE_URL)

        try:
            async with conn.transaction():
                # Update users table if name changed
                if update_data.name:
                    await conn.execute(
                        "UPDATE users SET name = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2",
                        update_data.name,
                        user_id
                    )

                # Build dynamic update query for user_profiles
                profile_updates = []
                profile_params = []
                param_index = 1

                if update_data.gpu_type:
                    profile_updates.append(f"gpu_type = ${param_index}")
                    profile_params.append(update_data.gpu_type)
                    param_index += 1

                if update_data.ram_capacity:
                    profile_updates.append(f"ram_capacity = ${param_index}")
                    profile_params.append(update_data.ram_capacity)
                    param_index += 1

                if update_data.coding_languages:
                    profile_updates.append(f"coding_languages = ${param_index}")
                    profile_params.append(json.dumps(update_data.coding_languages))
                    param_index += 1

                if update_data.robotics_experience:
                    profile_updates.append(f"robotics_experience = ${param_index}")
                    profile_params.append(update_data.robotics_experience)
                    param_index += 1

                # Update user_profiles if any hardware fields changed
                if profile_updates:
                    profile_updates.append(f"updated_at = CURRENT_TIMESTAMP")
                    profile_params.append(user_id)

                    update_query = f"""
                        UPDATE user_profiles
                        SET {', '.join(profile_updates)}
                        WHERE user_id = ${param_index}
                    """

                    await conn.execute(update_query, *profile_params)

                # Fetch complete updated profile
                user_data = await conn.fetchrow(
                    "SELECT id, email, name FROM users WHERE id = $1",
                    user_id
                )

                profile_data = await conn.fetchrow(
                    """
                    SELECT gpu_type, ram_capacity, coding_languages, robotics_experience
                    FROM user_profiles
                    WHERE user_id = $1
                    """,
                    user_id
                )

                if not user_data or not profile_data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User or profile not found"
                    )

                # Parse JSON field
                coding_languages = json.loads(profile_data["coding_languages"])

                # Create new JWT with updated profile claims
                new_token = create_access_token(
                    user_id=str(user_data["id"]),
                    email=user_data["email"],
                    name=user_data["name"],
                    gpu_type=profile_data["gpu_type"],
                    ram_capacity=profile_data["ram_capacity"],
                    coding_languages=coding_languages,
                    robotics_experience=profile_data["robotics_experience"]
                )

                # Log profile update
                logger.info(f"Profile updated for user: {user_id}")

                # Build response
                updated_profile = UserProfile(
                    id=str(user_data["id"]),
                    email=user_data["email"],
                    name=user_data["name"],
                    gpu_type=profile_data["gpu_type"],
                    ram_capacity=profile_data["ram_capacity"],
                    coding_languages=coding_languages,
                    robotics_experience=profile_data["robotics_experience"]
                )

                return ProfileUpdateResponse(
                    success=True,
                    message="Profile updated successfully. Please use the new token.",
                    profile=updated_profile,
                    token=new_token
                )

        finally:
            await conn.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed. Please try again later."
        )
