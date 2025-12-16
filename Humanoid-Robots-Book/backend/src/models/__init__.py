"""
Pydantic Models Package
Feature: 003-better-auth
Purpose: Export all request/response schemas for authentication and profile management
"""

from .auth import (
    SignupRequest,
    SigninRequest,
    AuthResponse,
    PasswordResetRequest,
    GPUType,
    RAMCapacity,
    CodingLanguage,
    RoboticsExperience
)

from .profile import (
    UserProfile,
    ProfileUpdateRequest,
    ProfileUpdateResponse
)

__all__ = [
    # Authentication schemas
    "SignupRequest",
    "SigninRequest",
    "AuthResponse",
    "PasswordResetRequest",

    # Profile schemas
    "UserProfile",
    "ProfileUpdateRequest",
    "ProfileUpdateResponse",

    # Enum types
    "GPUType",
    "RAMCapacity",
    "CodingLanguage",
    "RoboticsExperience",
]
