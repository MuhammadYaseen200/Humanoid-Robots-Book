"""
Authentication Utilities
Feature: 003-better-auth
Purpose: Password hashing and email enumeration prevention

CRITICAL: This module implements ADR-005 requirements:
- Async bcrypt wrapper (run_in_executor) to prevent event loop blocking
- Constant-time email verification to prevent enumeration attacks
"""

import asyncio
from passlib.context import CryptContext

# Initialize bcrypt password context with 12 salt rounds (ADR-005)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fake bcrypt hash for constant-time email enumeration prevention
# This is a valid bcrypt hash that we use when email doesn't exist
# so that we always perform bcrypt verification (same timing)
FAKE_PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU8bvbW5JQCW"


async def hash_password(plain_password: str) -> str:
    """
    Hash password using bcrypt with 12 salt rounds.

    **CRITICAL ADR-005 COMPLIANCE**:
    - Runs in executor to avoid blocking async event loop (~200-300ms)
    - Must NOT be called synchronously (will freeze entire backend)

    Args:
        plain_password: User's plaintext password

    Returns:
        Bcrypt hashed password starting with $2b$12$

    Raises:
        ValueError: If password is empty

    Performance:
        - ~200-300ms per hash (security requirement)
        - Non-blocking (runs in thread pool)

    Example:
        >>> hashed = await hash_password("SecurePass123!")
        >>> print(hashed)
        $2b$12$xyz...

    Reference:
        ADR-005 lines 232-256: Async wrapper MANDATORY to prevent event loop blocking
    """
    if not plain_password:
        raise ValueError("Password cannot be empty")

    # Run bcrypt in executor to prevent blocking event loop
    # This is CRITICAL - bcrypt is CPU-intensive and synchronous
    loop = asyncio.get_event_loop()
    hashed = await loop.run_in_executor(
        None,  # Use default executor (ThreadPoolExecutor)
        pwd_context.hash,
        plain_password
    )

    return hashed


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against bcrypt hash.

    **CRITICAL ADR-005 COMPLIANCE**:
    - Runs in executor to avoid blocking async event loop (~200-300ms)
    - Must NOT be called synchronously (will freeze entire backend)

    Args:
        plain_password: User's submitted password
        hashed_password: Stored bcrypt hash from database

    Returns:
        True if password matches hash, False otherwise

    Performance:
        - ~200-300ms per verification (security requirement)
        - Non-blocking (runs in thread pool)

    Example:
        >>> hashed = await hash_password("SecurePass123!")
        >>> is_valid = await verify_password("SecurePass123!", hashed)
        >>> assert is_valid == True
        >>> is_valid = await verify_password("WrongPassword", hashed)
        >>> assert is_valid == False

    Reference:
        ADR-005 lines 232-256: Async wrapper MANDATORY to prevent event loop blocking
    """
    if not plain_password or not hashed_password:
        return False

    # Run bcrypt verification in executor to prevent blocking event loop
    # This is CRITICAL - bcrypt.verify is CPU-intensive and synchronous
    loop = asyncio.get_event_loop()
    is_valid = await loop.run_in_executor(
        None,  # Use default executor (ThreadPoolExecutor)
        pwd_context.verify,
        plain_password,
        hashed_password
    )

    return is_valid


async def constant_time_verify(email: str, password: str, user_hash: str | None = None) -> bool:
    """
    Constant-time password verification to prevent email enumeration attacks.

    **CRITICAL ADR-005 COMPLIANCE**:
    - Always performs bcrypt verification (even if email doesn't exist)
    - Maintains constant response time (~300ms) regardless of email existence
    - Prevents timing attacks that reveal valid email addresses

    Args:
        email: User's submitted email
        password: User's submitted password
        user_hash: Password hash from database (None if email doesn't exist)

    Returns:
        True if email exists AND password matches, False otherwise

    Security:
        - If user_hash is None (email not found): Verifies against FAKE_PASSWORD_HASH
        - Always takes ~300ms regardless of whether email exists
        - Generic error message prevents information leakage

    Example:
        >>> # Email exists in database
        >>> is_valid = await constant_time_verify("user@example.com", "correct", db_hash)
        >>> # Takes ~300ms, returns True
        >>>
        >>> # Email doesn't exist
        >>> is_valid = await constant_time_verify("fake@example.com", "any", None)
        >>> # Takes ~300ms, returns False (same timing!)

    Reference:
        ADR-005 lines 283-316: Email enumeration prevention via constant-time responses
    """
    if user_hash is None:
        # Email doesn't exist: Use fake hash to maintain constant time
        # This ensures attacker cannot determine email existence by timing
        is_valid = await verify_password(password, FAKE_PASSWORD_HASH)
        return False  # Always return False for non-existent emails
    else:
        # Email exists: Verify against real hash
        is_valid = await verify_password(password, user_hash)
        return is_valid


# Additional utility functions for password validation

def check_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Check password strength and return feedback.

    Requirements (FR-005):
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one number
    - At least one symbol

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, list_of_errors)

    Example:
        >>> is_valid, errors = check_password_strength("weak")
        >>> print(errors)
        ['Password must be at least 8 characters',
         'Password must contain uppercase letter',
         'Password must contain number',
         'Password must contain symbol']
    """
    import re

    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one symbol (!@#$%^&*...)")

    is_valid = len(errors) == 0
    return is_valid, errors


def generate_secure_password(length: int = 16) -> str:
    """
    Generate a cryptographically secure random password.

    Args:
        length: Password length (minimum 16 recommended)

    Returns:
        Random password meeting all strength requirements

    Example:
        >>> password = generate_secure_password()
        >>> is_valid, _ = check_password_strength(password)
        >>> assert is_valid == True
    """
    import secrets
    import string

    # Ensure at least one character from each required category
    uppercase = secrets.choice(string.ascii_uppercase)
    lowercase = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    symbol = secrets.choice("!@#$%^&*(),.?\":{}|<>")

    # Fill remaining length with random characters from all categories
    remaining_length = length - 4
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*(),.?\":{}|<>"
    remaining = ''.join(secrets.choice(all_chars) for _ in range(remaining_length))

    # Combine and shuffle
    password_chars = list(uppercase + lowercase + digit + symbol + remaining)
    secrets.SystemRandom().shuffle(password_chars)

    return ''.join(password_chars)
