"""
Utilities Package
Feature: 003-better-auth
Purpose: Export authentication and JWT utilities
"""

from .auth import (
    hash_password,
    verify_password,
    constant_time_verify,
    check_password_strength,
    generate_secure_password
)

from .jwt import (
    create_access_token,
    decode_token,
    create_reset_token,
    decode_reset_token,
    extract_user_id_from_token,
    is_token_expired,
    get_token_expiration
)

__all__ = [
    # Password hashing (ADR-005 compliant - async wrappers)
    "hash_password",
    "verify_password",
    "constant_time_verify",
    "check_password_strength",
    "generate_secure_password",

    # JWT token management (ADR-006 compliant - embedded profile claims)
    "create_access_token",
    "decode_token",
    "create_reset_token",
    "decode_reset_token",
    "extract_user_id_from_token",
    "is_token_expired",
    "get_token_expiration",
]
