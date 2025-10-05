"""
Caso de uso: Obtener usuario actual
"""
from dataclasses import dataclass
from app.users.domain.user import User
from app.users.application.ports.user_repository import UserRepository
from app.building_blocks.exceptions import AuthenticationException


@dataclass
class GetCurrentUserCommand:
    """Comando para obtener usuario actual"""
    user_id: str


class GetCurrentUserUseCase:
    """
    Caso de uso: Obtener información del usuario actual.

    Este caso de uso obtiene la información del usuario autenticado.
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, command: GetCurrentUserCommand) -> User:
        user = await self.user_repository.find_by_id(command.user_id)

        if not user:
            raise AuthenticationException("Usuario no encontrado")

        return user
