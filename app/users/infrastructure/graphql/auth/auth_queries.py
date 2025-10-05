"""Queries GraphQL para autenticación"""
import strawberry
from strawberry.types import Info
from app.users.infrastructure.graphql.auth.auth_types import CurrentUserResponse
from app.building_blocks.exceptions import AuthenticationException


@strawberry.type
class AuthQueries:

    @strawberry.field
    async def me(
        self,
        info: Info
    ) -> CurrentUserResponse:
        """
        Obtiene información del usuario actual.
        Requiere autenticación (token JWT en header).
        """
        # Verificar que hay un usuario autenticado
        if not info.context["current_user"]:
            raise Exception("No autenticado. Debes incluir el token en el header Authorization")

        user = info.context["current_user"]

        return CurrentUserResponse(
            id=user.id,
            employee_id=user.employee_id,
            email=user.email,
            personal_email=user.personal_email,
            full_name=user.full_name,
            dni=user.dni,
            role=user.role.value,
            status=user.status.value,
            phone=user.phone,
            address=user.address
        )
