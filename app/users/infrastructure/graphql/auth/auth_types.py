"""Tipos GraphQL para autenticación"""
import strawberry
from typing import Optional

@strawberry.type
class UserInfo:
    """Información del usuario para respuestas de auth"""
    id: str
    email: str
    full_name: str
    role: str
    employee_id: str

@strawberry.type
class LoginResponse:
    """Respuesta del login"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserInfo

@strawberry.type
class RefreshTokenResponse:
    """Respuesta del refresh token"""
    access_token: str
    token_type: str
    expires_in: int

@strawberry.type
class LogoutResponse:
    """Respuesta del logout"""
    success: bool
    message: str

@strawberry.type
class CurrentUserResponse:
    """Respuesta con información del usuario actual"""
    id: str
    employee_id: str
    email: str
    personal_email: Optional[str]
    full_name: str
    dni: str
    role: str
    status: str
    phone: Optional[str]
    address: Optional[str]
