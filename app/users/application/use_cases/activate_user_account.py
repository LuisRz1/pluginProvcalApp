"""
Caso de uso: Activar cuenta de usuario.
"""
from dataclasses import dataclass

from app.users.application.ports.user_repository import UserRepository
from app.users.application.ports.activation_token_repository import ActivationTokenRepository
from app.users.application.ports.email_service import EmailService
from app.building_blocks.exceptions import DomainException


@dataclass
class ActivateUserAccountCommand:
    """Comando para activar cuenta de usuario"""
    token: str
    employee_id: str  # Validación de identidad
    password: str
    password_confirmation: str
    personal_email: str
    data_processing_consent: bool


class ActivateUserAccountUseCase:
    """
    Caso de uso: Activar cuenta de usuario.

    Este caso de uso:
    1. Valida el token de activación
    2. Valida el employee_id para verificar identidad
    3. Valida la contraseña
    4. Activa la cuenta del usuario
    5. Invalida el token
    6. Envía email de confirmación
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

    async def execute(self, command: ActivateUserAccountCommand) -> dict:
        # 1. Validar formato de contraseñas
        if command.password != command.password_confirmation:
            raise DomainException("Las contraseñas no coinciden")

        # 2. Buscar y validar token
        token = await self.token_repository.find_by_token(command.token)
        if not token:
            raise DomainException("Token de activación inválido")

        if not token.is_valid():
            if token.is_expired():
                raise DomainException("El token de activación ha expirado")
            raise DomainException("El token ya ha sido utilizado")

        # 3. Buscar usuario
        user = await self.user_repository.find_by_id(token.user_id)
        if not user:
            raise DomainException("Usuario no encontrado")

        # 4. Validar employee_id (verificación de identidad)
        if user.employee_id != command.employee_id:
            raise DomainException(
                "El ID de empleado proporcionado no coincide con el registrado"
            )

        # 5. Validar que el usuario pueda ser activado
        if not user.can_activate():
            raise DomainException(
                f"La cuenta no puede ser activada. Estado actual: {user.status.value}"
            )

        # 6. Activar cuenta (esto también establece la contraseña)
        user.activate(
            password=command.password,
            personal_email=command.personal_email,
            data_consent=command.data_processing_consent
        )

        # 7. Guardar usuario actualizado
        updated_user = await self.user_repository.save(user)

        # 8. Marcar token como usado
        token.mark_as_used()
        await self.token_repository.save(token)

        # 9. Invalidar otros tokens del usuario (si existieran)
        await self.token_repository.invalidate_user_tokens(user.id)

        # 10. Enviar email de confirmación
        await self.email_service.send_account_activated_email(
            to_email=updated_user.email,
            user_name=updated_user.full_name
        )

        return {
            "user_id": updated_user.id,
            "email": updated_user.email,
            "status": updated_user.status.value,
            "activated_at": updated_user.activated_at.isoformat() if updated_user.activated_at else None
        }
