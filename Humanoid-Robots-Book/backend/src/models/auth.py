"""
Authentication Request/Response Models
Feature: 003-better-auth
Purpose: Pydantic schemas for signup, signin, and authentication responses
"""

from typing import List
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class SignupRequest(BaseModel):
    """
    User signup request with hardware profiling.

    **The 50-Point Hackathon Feature**: Hardware background questions
    are asked during signup to enable personalized content recommendations.
    """
    # Basic authentication fields
    email: EmailStr = Field(
        ...,
        description="User email address (must be valid format)",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (8-128 characters, must include uppercase, lowercase, and number)",
        examples=["MySecurePass123!"]
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="User's full name",
        examples=["John Doe"]
    )

    # Hardware Profile Fields (THE HACKATHON BONUS FEATURE)
    gpu_type: str = Field(
        ...,
        description="GPU type for running robotics simulations",
        examples=["NVIDIA RTX 4070 Ti"]
    )
    ram_capacity: str = Field(
        ...,
        description="System RAM capacity",
        examples=["16-32GB"]
    )
    coding_languages: List[str] = Field(
        ...,
        min_length=1,
        description="Programming languages user knows",
        examples=[["Python", "C++"]]
    )
    robotics_experience: str = Field(
        ...,
        description="Level of robotics experience",
        examples=["Beginner (0-1 years)"]
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength.
        Requirements:
        - At least 8 characters
        - Contains uppercase letter
        - Contains lowercase letter
        - Contains number
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v

    @field_validator("gpu_type")
    @classmethod
    def validate_gpu_type(cls, v: str) -> str:
        """Validate GPU type against allowed values."""
        allowed_values = {
            "No GPU",
            "NVIDIA RTX 3060",
            "NVIDIA RTX 4070 Ti",
            "NVIDIA RTX 4090",
            "Apple M1/M2/M3",
            "Other"
        }
        if v not in allowed_values:
            raise ValueError(f"GPU type must be one of: {', '.join(allowed_values)}")
        return v

    @field_validator("ram_capacity")
    @classmethod
    def validate_ram_capacity(cls, v: str) -> str:
        """Validate RAM capacity against allowed values."""
        allowed_values = {
            "Less than 8GB",
            "8-16GB",
            "16-32GB",
            "More than 32GB"
        }
        if v not in allowed_values:
            raise ValueError(f"RAM capacity must be one of: {', '.join(allowed_values)}")
        return v

    @field_validator("robotics_experience")
    @classmethod
    def validate_robotics_experience(cls, v: str) -> str:
        """Validate robotics experience level."""
        allowed_values = {
            "No prior experience",
            "Beginner (0-1 years)",
            "Intermediate (1-3 years)",
            "Advanced (3+ years)"
        }
        if v not in allowed_values:
            raise ValueError(f"Robotics experience must be one of: {', '.join(allowed_values)}")
        return v


class SigninRequest(BaseModel):
    """User signin request."""
    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        description="User password",
        examples=["MySecurePass123!"]
    )


class AuthResponse(BaseModel):
    """
    Authentication response with JWT token and user profile.

    **ADR-006 Decision**: JWT embeds profile claims for stateless personalization.
    Token size: ~500 bytes (well under 4KB cookie limit).
    """
    success: bool = Field(
        ...,
        description="Whether authentication succeeded"
    )
    message: str = Field(
        ...,
        description="Human-readable message",
        examples=["Signup successful. Welcome!"]
    )
    token: str = Field(
        ...,
        description="JWT access token (expires in 24 hours)",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    user: dict = Field(
        ...,
        description="User profile data",
        examples=[{
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "name": "John Doe",
            "gpu_type": "NVIDIA RTX 4070 Ti",
            "ram_capacity": "16-32GB",
            "coding_languages": ["Python", "C++"],
            "robotics_experience": "Beginner (0-1 years)"
        }]
    )


class SignoutRequest(BaseModel):
    """User signout request (for logging purposes)."""
    user_id: str = Field(
        ...,
        description="User ID from JWT token"
    )
