import strawberry
from typing import Optional

@strawberry.input
class CreateUserAccountInput:
    """Input para crear cuenta de usuario (solo admin)"""
    employee_id: str
    email: str
    full_name: str
    dni: str
    role: str  # "employee", "cook", "nutritionist", "warehouse"
    phone: Optional[str] = None
    address: Optional[str] = None
    activation_base_url: str = ""

@strawberry.input
class ActivateUserAccountInput:
    """Input para activar cuenta de usuario"""
    token: str
    employee_id: str
    password: str
    password_confirmation: str
    personal_email: str
    data_processing_consent: bool

@strawberry.input
class ValidateActivationTokenInput:
    """Input para validar token de activación"""
    token: str
