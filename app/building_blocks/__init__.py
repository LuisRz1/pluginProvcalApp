"""
Building blocks para Domain-Driven Design.
"""

from app.building_blocks.exceptions import (
    DomainException,
    ValidationException,
    AuthorizationException,
    AuthenticationException,
    NotFoundException,
    ConflictException
)

__all__ = [
    "DomainException",
    "ValidationException",
    "AuthorizationException",
    "AuthenticationException",
    "NotFoundException",
    "ConflictException",
]