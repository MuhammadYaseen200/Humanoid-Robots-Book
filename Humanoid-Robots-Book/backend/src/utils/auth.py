"""
Password Hashing Utilities
Feature: 003-better-auth
Purpose: Async-safe bcrypt password hashing

**ADR-005 Decision**: Use bcrypt with async wrapper to prevent event loop blocking.
Bcrypt operations (~200-300ms) run in thread pool executor to avoid blocking FastAPI.
"""

from passlib.context import CryptContext
import asyncio
from functools import partial

# Configure bcrypt context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def hash_password(password: str) -> str:
    """
    Hash password using bcrypt in a thread pool.

    **Performance**: Bcrypt hashing takes ~200-300ms. Running in thread pool
    prevents blocking the FastAPI event loop during user signup.

    Args:
        password: Plain text password

    Returns:
        str: Bcrypt hash (60 characters, starts with $2b$)

    Example:
        >>> hash_val = await hash_password("MySecurePass123!")
        >>> assert len(hash_val) == 60
        >>> assert hash_val.startswith("$2b$")
    """
    loop = asyncio.get_event_loop()
    hash_func = partial(pwd_context.hash, password)
    return await loop.run_in_executor(None, hash_func)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against bcrypt hash in a thread pool.

    **Performance**: Bcrypt verification takes ~200-300ms. Running in thread pool
    prevents blocking the event loop during user signin.

    **Security**: Constant-time comparison prevents timing attacks.

    Args:
        plain_password: Plain text password from signin request
        hashed_password: Bcrypt hash from database

    Returns:
        bool: True if password matches, False otherwise

    Example:
        >>> hash_val = await hash_password("MySecurePass123!")
        >>> assert await verify_password("MySecurePass123!", hash_val) == True
        >>> assert await verify_password("WrongPassword", hash_val) == False
    """
    loop = asyncio.get_event_loop()
    verify_func = partial(pwd_context.verify, plain_password, hashed_password)
    return await loop.run_in_executor(None, verify_func)
