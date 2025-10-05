"""
Caso de uso: Validar token de activación.
"""
from dataclasses import dataclass
from typing import Optional

from app.users.application.ports.activation_token_repository import ActivationTokenRepository
from app.users.application.ports.user_repository import UserRepository


@dataclass
class ValidateActivationTokenCommand:
    """Comando para validar un token de activación"""
    token: str


class ValidateActivationTokenUseCase:
    """
    Caso de uso: Validar token de activación.

    Este caso de uso permite verificar si un token es válido
    antes de mostrar el formulario de activación.
    """

    def __init__(
        self,
        token_repository: ActivationTokenRepository,
        user_repository: UserRepository
    ):
        self.token_repository = token_repository
        self.user_repository = user_repository

    async def execute(self, command: ValidateActivationTokenCommand) -> dict:
        # 1. Buscar token
        token = await self.token_repository.find_by_token(command.token)

        if not token:
            return {
                "is_valid": False,
                "reason": "Token no encontrado"
            }

        # 2. Verificar si el token es válido
        if not token.is_valid():
            if token.is_expired():
                reason = "Token expirado"
            else:
                reason = "Token ya utilizado"

            return {
                "is_valid": False,
                "reason": reason,
                "expired_at": token.expires_at.isoformat() if token.is_expired() else None
            }

        # 3. Buscar usuario asociado
        user = await self.user_repository.find_by_id(token.user_id)

        if not user:
            return {
                "is_valid": False,
                "reason": "Usuario no encontrado"
            }

        # 4. Verificar estado del usuario
        if not user.can_activate():
            return {
                "is_valid": False,
                "reason": f"Usuario en estado: {user.status.value}"
            }

        # 5. Token válido, devolver información para el formulario
        return {
            "is_valid": True,
            "user": {
                "email": user.email,
                "full_name": user.full_name,
                "employee_id": user.employee_id  # Opcional: podrías no devolverlo por seguridad
            },
            "expires_at": token.expires_at.isoformat()
        }
