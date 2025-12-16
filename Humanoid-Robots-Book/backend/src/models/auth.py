"""
Authentication Pydantic Models
Feature: 003-better-auth
Purpose: Request/response schemas for authentication endpoints
"""

from typing import List, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

# Enum types matching database CHECK constraints
GPUType = Literal[
    "None/Integrated Graphics",
    "NVIDIA RTX 3060",
    "NVIDIA RTX 4070 Ti",
    "NVIDIA RTX 4080/4090",
    "AMD Radeon RX 7000 Series",
    "Other"
]

RAMCapacity = Literal[
    "4-8GB",
    "8-16GB",
    "16-32GB",
    "32GB or more"
]

CodingLanguage = Literal[
    "None",
    "Python",
    "C++",
    "JavaScript/TypeScript",
    "Java",
    "C#",
    "Rust",
    "Other"
]

RoboticsExperience = Literal[
    "No prior experience",
    "Hobbyist (built simple projects)",
    "Student (taking courses)",
    "Professional (industry experience)"
]


class SignupRequest(BaseModel):
    """
    Request model for POST /api/auth/signup
    All fields are required for 100% profile completeness (FR-019)
    """
    # Authentication fields
    email: EmailStr = Field(
        ...,
        max_length=255,
        description="User email address (must be unique)",
        json_schema_extra={"example": "student@example.com"}
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (min 8 chars, must contain uppercase, number, symbol)",
        json_schema_extra={"example": "SecurePass123!"}
    )
    name: str = Field(
        ...,
        max_length=255,
        description="User display name",
        json_schema_extra={"example": "John Doe"}
    )

    # Hardware/Software Profile fields (THE 50-POINT FEATURE)
    gpu_type: GPUType = Field(
        ...,
        description="User GPU hardware type",
        json_schema_extra={"example": "NVIDIA RTX 4070 Ti"}
    )
    ram_capacity: RAMCapacity = Field(
        ...,
        description="User system RAM capacity",
        json_schema_extra={"example": "16-32GB"}
    )
    coding_languages: List[CodingLanguage] = Field(
        ...,
        min_length=1,
        description="Programming languages user knows (at least one required)",
        json_schema_extra={"example": ["Python", "C++"]}
    )
    robotics_experience: RoboticsExperience = Field(
        ...,
        description="User robotics background level",
        json_schema_extra={"example": "Hobbyist (built simple projects)"}
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets security requirements (FR-005):
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one number
        - At least one symbol
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r'[0-9]', v):
            raise ValueError("Password must contain at least one number")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one symbol (!@#$%^&*...)")

        return v

    @field_validator('coding_languages')
    @classmethod
    def validate_coding_languages(cls, v: List[CodingLanguage]) -> List[CodingLanguage]:
        """
        Validate at least one coding language selected
        """
        if not v or len(v) == 0:
            raise ValueError("At least one coding language must be selected")
        return v

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """
        Convert email to lowercase for case-insensitive comparison (FR-004)
        """
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "SecurePass123!",
                "name": "John Doe",
                "gpu_type": "NVIDIA RTX 4070 Ti",
                "ram_capacity": "16-32GB",
                "coding_languages": ["Python", "C++"],
                "robotics_experience": "Hobbyist (built simple projects)"
            }
        }


class SigninRequest(BaseModel):
    """
    Request model for POST /api/auth/signin
    Simple email/password authentication
    """
    email: EmailStr = Field(
        ...,
        description="User email address",
        json_schema_extra={"example": "student@example.com"}
    )
    password: str = Field(
        ...,
        description="User password",
        json_schema_extra={"example": "SecurePass123!"}
    )

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """
        Convert email to lowercase for case-insensitive comparison
        """
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "SecurePass123!"
            }
        }


class AuthResponse(BaseModel):
    """
    Response model for successful authentication
    Returns JWT token and user profile
    """
    token: str = Field(
        ...,
        description="JWT token (also in httpOnly cookie if production)",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )
    user: 'UserProfile' = Field(
        ...,
        description="User profile information"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "student@example.com",
                    "name": "John Doe",
                    "gpu_type": "NVIDIA RTX 4070 Ti",
                    "ram_capacity": "16-32GB",
                    "coding_languages": ["Python", "C++"],
                    "robotics_experience": "Hobbyist (built simple projects)",
                    "created_at": "2025-12-16T10:30:00Z"
                }
            }
        }


class PasswordResetRequest(BaseModel):
    """
    Request model for POST /api/auth/reset-password
    Used with reset token from email link
    """
    token: str = Field(
        ...,
        description="Password reset JWT token from email link"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (same validation as signup)"
    )

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets security requirements (same as SignupRequest)
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r'[0-9]', v):
            raise ValueError("Password must contain at least one number")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one symbol (!@#$%^&*...)")

        return v


# Import UserProfile after class definitions to avoid circular import
from .profile import UserProfile

# Update forward references
AuthResponse.model_rebuild()
