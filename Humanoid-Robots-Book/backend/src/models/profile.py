"""
User Profile Pydantic Models
Feature: 003-better-auth
Purpose: User profile schemas for GET/PUT /api/profile endpoints
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from .auth import GPUType, RAMCapacity, CodingLanguage, RoboticsExperience


class UserProfile(BaseModel):
    """
    Response model for GET /api/profile and user data in AuthResponse
    Represents complete user profile with all fields
    """
    id: str = Field(
        ...,
        description="User UUID",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"}
    )
    email: EmailStr = Field(
        ...,
        description="User email address",
        json_schema_extra={"example": "student@example.com"}
    )
    name: str = Field(
        ...,
        description="User display name",
        json_schema_extra={"example": "John Doe"}
    )

    # Hardware/Software Profile fields (from JWT claims)
    gpu_type: str = Field(
        ...,
        description="User GPU hardware type",
        json_schema_extra={"example": "NVIDIA RTX 4070 Ti"}
    )
    ram_capacity: str = Field(
        ...,
        description="User system RAM capacity",
        json_schema_extra={"example": "16-32GB"}
    )
    coding_languages: List[str] = Field(
        ...,
        description="Programming languages user knows",
        json_schema_extra={"example": ["Python", "C++"]}
    )
    robotics_experience: str = Field(
        ...,
        description="User robotics background level",
        json_schema_extra={"example": "Hobbyist (built simple projects)"}
    )

    # Additional profile fields (not in JWT, from database)
    learning_style: Optional[str] = Field(
        default="balanced",
        description="Learning preference (visual/auditory/kinesthetic)",
        json_schema_extra={"example": "balanced"}
    )
    difficulty_level: Optional[str] = Field(
        default="intermediate",
        description="Current skill level",
        json_schema_extra={"example": "intermediate"}
    )
    preferred_language: Optional[str] = Field(
        default="en",
        description="UI language (en/ur)",
        json_schema_extra={"example": "en"}
    )

    # Timestamps
    created_at: datetime = Field(
        ...,
        description="Account creation timestamp",
        json_schema_extra={"example": "2025-12-16T10:30:00Z"}
    )
    last_login: Optional[datetime] = Field(
        default=None,
        description="Most recent signin timestamp",
        json_schema_extra={"example": "2025-12-16T14:45:00Z"}
    )

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy compatibility
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "student@example.com",
                "name": "John Doe",
                "gpu_type": "NVIDIA RTX 4070 Ti",
                "ram_capacity": "16-32GB",
                "coding_languages": ["Python", "C++"],
                "robotics_experience": "Hobbyist (built simple projects)",
                "learning_style": "balanced",
                "difficulty_level": "intermediate",
                "preferred_language": "en",
                "created_at": "2025-12-16T10:30:00Z",
                "last_login": "2025-12-16T14:45:00Z"
            }
        }


class ProfileUpdateRequest(BaseModel):
    """
    Request model for PUT /api/profile
    Allows updating hardware/software profile fields
    Email cannot be changed (permanent identifier - FR-026)
    """
    gpu_type: Optional[GPUType] = Field(
        default=None,
        description="User GPU hardware type"
    )
    ram_capacity: Optional[RAMCapacity] = Field(
        default=None,
        description="User system RAM capacity"
    )
    coding_languages: Optional[List[CodingLanguage]] = Field(
        default=None,
        min_length=1,
        description="Programming languages user knows"
    )
    robotics_experience: Optional[RoboticsExperience] = Field(
        default=None,
        description="User robotics background level"
    )

    # Additional profile fields (optional)
    learning_style: Optional[str] = Field(
        default=None,
        description="Learning preference"
    )
    difficulty_level: Optional[str] = Field(
        default=None,
        description="Current skill level"
    )
    preferred_language: Optional[str] = Field(
        default=None,
        description="UI language (en/ur)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "gpu_type": "NVIDIA RTX 4070 Ti",
                "ram_capacity": "16-32GB",
                "coding_languages": ["Python", "C++", "Rust"],
                "robotics_experience": "Student (taking courses)"
            }
        }


class ProfileUpdateResponse(BaseModel):
    """
    Response model for PUT /api/profile
    Returns updated profile and refreshed JWT token with new claims
    """
    user: UserProfile = Field(
        ...,
        description="Updated user profile"
    )
    token: str = Field(
        ...,
        description="Refreshed JWT token with updated profile claims",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "student@example.com",
                    "name": "John Doe",
                    "gpu_type": "NVIDIA RTX 4070 Ti",
                    "ram_capacity": "16-32GB",
                    "coding_languages": ["Python", "C++", "Rust"],
                    "robotics_experience": "Student (taking courses)",
                    "learning_style": "balanced",
                    "difficulty_level": "intermediate",
                    "preferred_language": "en",
                    "created_at": "2025-12-16T10:30:00Z",
                    "last_login": "2025-12-16T14:45:00Z"
                },
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
