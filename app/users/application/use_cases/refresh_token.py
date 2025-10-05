"""
Caso de uso: Refrescar token de acceso
"""
from dataclasses import dataclass
from app.users.application.ports.user_repository import UserRepository
from app.users.application.ports.auth_service import AuthService
from app.building_blocks.exceptions import AuthenticationException


@dataclass
class RefreshTokenCommand:
    """Comando para refrescar token"""
    refresh_token: str


class RefreshTokenUseCase:
    """
    Caso de uso: Refrescar access token.

    Este caso de uso:
    1. Valida el refresh token
    2. Verifica que el usuario siga activo
    3. Genera un nuevo access token
    """

    def __init__(
        self,
        user_repository: UserRepository,
        auth_service: AuthService
    ):
        self.user_repository = user_repository
        self.auth_service = auth_service

    async def execute(self, command: RefreshTokenCommand) -> dict:
        # 1. Verificar refresh token
        payload = await self.auth_service.verify_token(command.refresh_token)

        if not payload:
            raise AuthenticationException("Refresh token inválido o expirado")

        # 2. Verificar que sea un refresh token
        if payload.get("type") != "refresh":
            raise AuthenticationException("Token inválido")

        # 3. Obtener usuario
        user_id = payload.get("sub")
        user = await self.user_repository.find_by_id(user_id)

        if not user:
            raise AuthenticationException("Usuario no encontrado")

        # 4. Verificar que el usuario esté activo
        from app.users.domain.user import UserStatus
        if user.status != UserStatus.ACTIVE:
            raise AuthenticationException("Usuario inactivo")

        # 5. Generar nuevo access token
        access_token = await self.auth_service.generate_access_token(user)

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 1800
        }