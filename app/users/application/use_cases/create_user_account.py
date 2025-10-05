"""
Caso de uso: Crear cuenta de usuario por parte del administrador.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.users.domain.user import User, UserRole, UserStatus
from app.users.domain.activation_token import ActivationToken

from app.users.application.ports.user_repository import UserRepository
from app.users.application.ports.activation_token_repository import ActivationTokenRepository
from app.users.application.ports.email_service import EmailService
from app.building_blocks.exceptions import DomainException


@dataclass
class CreateUserAccountCommand:
    """Comando para crear una cuenta de usuario (ejecutado por admin)"""
    employee_id: str
    email: str  # Email corporativo
    full_name: str
    dni: str
    role: UserRole
    phone: Optional[str] = None
    address: Optional[str] = None
    created_by: Optional[str] = None  # ID del admin
    activation_base_url: str = ""  # URL base para el link de activación


class CreateUserAccountUseCase:
    """
    Caso de uso: Crear cuenta de usuario por parte del administrador.

    Este caso de uso:
    1. Valida que no exista el usuario
    2. Crea el usuario en estado PENDING_ACTIVATION
    3. Genera un token de activación seguro
    4. Envía email con link de activación
    """

    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: ActivationTokenRepository,
        email_service: EmailService
    ):
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.email_service = email_service

    async def execute(self, command: CreateUserAccountCommand) -> dict:
        # 1. Validar que no exista el usuario
        await self._validate_user_not_exists(command.employee_id, command.email)

        # 2. Crear usuario en estado pendiente
        user = User(
            employee_id=command.employee_id,
            email=command.email,
            full_name=command.full_name,
            dni=command.dni,
            role=command.role,
            phone=command.phone,
            address=command.address,
            status=UserStatus.PENDING_ACTIVATION,
            created_by=command.created_by,
            created_at=datetime.now(timezone.utc)
        )

        # 3. Guardar usuario
        saved_user = await self.user_repository.save(user)

        # 4. Generar token de activación
        token = ActivationToken(
            token=ActivationToken.generate_secure_token(),
            user_id=saved_user.id,
            employee_id=saved_user.employee_id,
            created_at=datetime.now(timezone.utc)
        )

        # 5. Guardar token
        saved_token = await self.token_repository.save(token)

        # 6. Construir link de activación
        activation_link = f"{command.activation_base_url}/activate?token={saved_token.token}"

        # 7. Enviar email de activación
        email_sent = await self.email_service.send_activation_email(
            to_email=saved_user.email,
            user_name=saved_user.full_name,
            activation_link=activation_link,
            expires_in_hours=48
        )

        if not email_sent:
            raise DomainException("No se pudo enviar el email de activación")

        return {
            "user_id": saved_user.id,
            "employee_id": saved_user.employee_id,
            "email": saved_user.email,
            "status": saved_user.status.value,
            "activation_token_expires_at": saved_token.expires_at.isoformat()
        }

    async def _validate_user_not_exists(self, employee_id: str, email: str) -> None:
        """Valida que no exista un usuario con el mismo employee_id o email"""
        if await self.user_repository.exists_by_employee_id(employee_id):
            raise DomainException(
                f"Ya existe un usuario con el employee_id: {employee_id}"
            )

        if await self.user_repository.exists_by_email(email):
            raise DomainException(
                f"Ya existe un usuario con el email: {email}"
            )


