"""
FastAPI Dependencies for Authentication
Feature: 003-better-auth
"""

from .auth import get_current_user, get_current_user_id

__all__ = [
    "get_current_user",
    "get_current_user_id",
]
