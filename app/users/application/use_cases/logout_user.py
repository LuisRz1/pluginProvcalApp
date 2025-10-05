"""
Caso de uso: Logout de usuario
"""
from dataclasses import dataclass


@dataclass
class LogoutUserCommand:
    """Comando para logout"""
    user_id: str


class LogoutUserUseCase:
    """
    Caso de uso: Logout de usuario.

    En una implementación con JWT stateless, el logout se maneja en el cliente
    eliminando los tokens. Si quieres implementar una blacklist de tokens,
    necesitarías un repositorio adicional para tokens revocados.
    """

    async def execute(self, command: LogoutUserCommand) -> dict:
        # En JWT stateless, el logout se maneja en el cliente
        # El cliente debe eliminar los tokens del almacenamiento local

        # Opcional: Implementar blacklist de tokens
        # await self.token_blacklist_repository.add(command.access_token)

        return {
            "success": True,
            "message": "Sesión cerrada exitosamente"
        }