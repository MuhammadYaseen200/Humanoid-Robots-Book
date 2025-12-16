"""
FastAPI Dependencies Package
Feature: 003-better-auth
Purpose: Export authentication dependencies for route protection
"""

from .auth import (
    get_current_user,
    get_current_user_id,
    get_optional_user,
    get_current_user_from_cookie,
)

__all__ = [
    "get_current_user",
    "get_current_user_id",
    "get_optional_user",
    "get_current_user_from_cookie",
]
