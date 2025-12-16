"""
Routers Package
Feature: 003-better-auth
Purpose: Export all API routers for registration in main.py
"""

from .auth import router as auth_router
from .profile import router as profile_router

__all__ = [
    "auth_router",
    "profile_router",
]
