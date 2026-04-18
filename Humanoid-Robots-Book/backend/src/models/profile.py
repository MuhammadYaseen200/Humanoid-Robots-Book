"""
User Profile Models
Feature: 003-better-auth
Purpose: Pydantic schemas for user profile management
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """
    User profile with hardware background information.

    This model represents the complete user profile including
    hardware specs used for content personalization.
    """
    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User's full name")

    # Hardware Profile Fields
    gpu_type: str = Field(..., description="GPU type")
    ram_capacity: str = Field(..., description="RAM capacity")
    coding_languages: List[str] = Field(..., description="Programming languages")
    robotics_experience: str = Field(..., description="Robotics experience level")


class ProfileUpdateRequest(BaseModel):
    """
    Profile update request.

    Allows users to update their hardware profile and personal information.
    All fields are optional - only provided fields will be updated.
    """
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Updated name"
    )
    gpu_type: Optional[str] = Field(
        None,
        description="Updated GPU type"
    )
    ram_capacity: Optional[str] = Field(
        None,
        description="Updated RAM capacity"
    )
    coding_languages: Optional[List[str]] = Field(
        None,
        description="Updated coding languages"
    )
    robotics_experience: Optional[str] = Field(
        None,
        description="Updated robotics experience level"
    )


class ProfileUpdateResponse(BaseModel):
    """
    Profile update response.

    Returns success status, message, updated profile, and new JWT token
    (since profile claims are embedded in the token per ADR-006).
    """
    success: bool = Field(..., description="Whether update succeeded")
    message: str = Field(..., description="Human-readable message")
    profile: UserProfile = Field(..., description="Updated user profile")
    token: str = Field(
        ...,
        description="New JWT token with updated profile claims"
    )
