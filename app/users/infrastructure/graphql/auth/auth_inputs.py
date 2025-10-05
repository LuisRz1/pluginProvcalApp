"""Inputs GraphQL para autenticación"""
import strawberry

@strawberry.input
class LoginInput:
    """Input para login"""
    email: str
    password: str

@strawberry.input
class RefreshTokenInput:
    """Input para refresh token"""
    refresh_token: str
