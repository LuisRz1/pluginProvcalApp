"""Module providing ..."""
from typing import Optional
from datetime import datetime
import strawberry

@strawberry.type
class UserType:
    """Tipo GraphQL para Usuario"""
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
    data_processing_consent: bool
    created_at: datetime
    activated_at: Optional[datetime]

@strawberry.type
class CreateUserAccountResult:
    """Resultado de crear cuenta de usuario"""
    success: bool
    message: str
    user_id: Optional[str] = None
    employee_id: Optional[str] = None
    email: Optional[str] = None
    activation_token_expires_at: Optional[str] = None

@strawberry.type
class ActivateUserAccountResult:
    """Resultado de activar cuenta de usuario"""
    success: bool
    message: str
    user_id: Optional[str] = None
    email: Optional[str] = None

@strawberry.type
class UserForActivation:
    """Información del usuario para mostrar en formulario de activación"""
    email: str
    full_name: str
    employee_id: Optional[str] = None  # Opcional por seguridad

@strawberry.type
class ValidateActivationTokenResult:
    """Resultado de validar token de activación"""
    is_valid: bool
    reason: Optional[str] = None
    user: Optional[UserForActivation] = None
    expires_at: Optional[str] = None