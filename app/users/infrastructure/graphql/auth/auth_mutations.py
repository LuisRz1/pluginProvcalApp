"""Mutations GraphQL para autenticación"""
import strawberry
from strawberry.types import Info

from app.users.infrastructure.graphql.auth.auth_inputs import LoginInput, RefreshTokenInput
from app.users.infrastructure.graphql.auth.auth_types import (
    LoginResponse,
    RefreshTokenResponse,
    LogoutResponse,
    UserInfo
)
from app.users.application.use_cases.login_user import (
    LoginUserUseCase,
    LoginUserCommand
)
from app.users.application.use_cases.refresh_token import (
    RefreshTokenUseCase,
    RefreshTokenCommand
)
from app.users.application.use_cases.logout_user import (
    LogoutUserUseCase,
    LogoutUserCommand
)
from app.building_blocks.exceptions import AuthenticationException


@strawberry.type
class AuthMutations:

    @strawberry.mutation
    async def login(
        self,
        info: Info,
        input: LoginInput
    ) -> LoginResponse:
        """
        Login de usuario.
        Devuelve access token y refresh token.
        """
        try:
            # Crear comando
            command = LoginUserCommand(
                email=input.email,
                password=input.password
            )

            # Ejecutar caso de uso
            use_case = LoginUserUseCase(
                user_repository=info.context["user_repository"],
                auth_service=info.context["auth_service"]
            )

            result = await use_case.execute(command)

            # Convertir respuesta
            return LoginResponse(
                access_token=result.access_token,
                refresh_token=result.refresh_token,
                token_type=result.token_type,
                expires_in=result.expires_in,
                user=UserInfo(
                    id=result.user["id"],
                    email=result.user["email"],
                    full_name=result.user["full_name"],
                    role=result.user["role"],
                    employee_id=result.user["employee_id"]
                )
            )

        except AuthenticationException as e:
            raise Exception(str(e))
        except Exception as e:
            raise Exception(f"Error en login: {str(e)}")

    @strawberry.mutation
    async def refresh_token(
        self,
        info: Info,
        input: RefreshTokenInput
    ) -> RefreshTokenResponse:
        """
        Refresca el access token usando un refresh token válido.
        """
        try:
            # Crear comando
            command = RefreshTokenCommand(
                refresh_token=input.refresh_token
            )

            # Ejecutar caso de uso
            use_case = RefreshTokenUseCase(
                user_repository=info.context["user_repository"],
                auth_service=info.context["auth_service"]
            )

            result = await use_case.execute(command)

            return RefreshTokenResponse(
                access_token=result["access_token"],
                token_type=result["token_type"],
                expires_in=result["expires_in"]
            )

        except AuthenticationException as e:
            raise Exception(str(e))
        except Exception as e:
            raise Exception(f"Error al refrescar token: {str(e)}")

    @strawberry.mutation
    async def logout(
        self,
        info: Info
    ) -> LogoutResponse:
        """
        Cierra la sesión del usuario actual.
        Requiere autenticación.
        """
        try:
            # Verificar que hay un usuario autenticado
            if not info.context["current_user"]:
                raise AuthenticationException("No autenticado")

            # Crear comando
            command = LogoutUserCommand(
                user_id=info.context["current_user"].id
            )

            # Ejecutar caso de uso
            use_case = LogoutUserUseCase()
            result = await use_case.execute(command)

            return LogoutResponse(
                success=result["success"],
                message=result["message"]
            )

        except AuthenticationException as e:
            raise Exception(str(e))
        except Exception as e:
            raise Exception(f"Error en logout: {str(e)}")

