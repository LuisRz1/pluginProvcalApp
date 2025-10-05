"""
Caso de uso: Login de usuario
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone

from app.users.application.ports.user_repository import UserRepository
from app.users.application.ports.auth_service import AuthService
from app.building_blocks.exceptions import AuthenticationException, DomainException


@dataclass
class LoginUserCommand:
    """Comando para login de usuario"""
    email: str
    password: str


@dataclass
class LoginUserResponse:
    """Respuesta del login"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 1800  # 30 minutos en segundos
    user: dict = None


class LoginUserUseCase:
    """
    Caso de uso: Login de usuario.

    Este caso de uso:
    1. Valida las credenciales (email y contraseña)
    2. Verifica que el usuario esté activo
    3. Genera tokens JWT (access y refresh)
    4. Actualiza la fecha de último login
    """

    def __init__(
        self,
        user_repository: UserRepository,
        auth_service: AuthService
    ):
        self.user_repository = user_repository
        self.auth_service = auth_service

    async def execute(self, command: LoginUserCommand) -> LoginUserResponse:
        # 1. Buscar usuario por email
        user = await self.user_repository.find_by_email(command.email)

        if not user:
            raise AuthenticationException("Credenciales inválidas")

        # 2. Verificar contraseña
        if not user.verify_password(command.password):
            raise AuthenticationException("Credenciales inválidas")

        # 3. Verificar que la cuenta esté activa
        from app.users.domain.user import UserStatus
        if user.status != UserStatus.ACTIVE:
            raise AuthenticationException(
                f"La cuenta no está activa. Estado: {user.status.value}"
            )

        # 4. Generar tokens
        access_token = await self.auth_service.generate_access_token(user)
        refresh_token = await self.auth_service.generate_refresh_token(user)

        # 5. Actualizar último login (opcional, agregar campo a User si lo necesitas)
        # user.last_login = datetime.now(timezone.utc)
        # await self.user_repository.save(user)

        # 6. Preparar respuesta
        return LoginUserResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=1800,  # 30 minutos
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "employee_id": user.employee_id
            }
        )