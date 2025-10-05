import strawberry
from strawberry.types import Info
from app.users.infrastructure.graphql.inputs import ValidateActivationTokenInput
from app.users.infrastructure.graphql.types import (
    ValidateActivationTokenResult,
    UserForActivation
)
from app.users.application.use_cases.validate_activation_token import (
    ValidateActivationTokenUseCase,
    ValidateActivationTokenCommand
)

@strawberry.type
class UserQueries:

    @strawberry.field
    async def validate_activation_token(
        self,
        info: Info,
        input: ValidateActivationTokenInput
    ) -> ValidateActivationTokenResult:
        """
        Valida un token de activación.
        Esta query NO requiere autenticación (es pública).
        Útil para verificar el token antes de mostrar el formulario.
        """
        try:
            # Crear comando
            command = ValidateActivationTokenCommand(
                token=input.token
            )

            # Ejecutar caso de uso
            use_case = ValidateActivationTokenUseCase(
                token_repository=info.context["token_repository"],
                user_repository=info.context["user_repository"]
            )

            result = await use_case.execute(command)

            if not result["is_valid"]:
                return ValidateActivationTokenResult(
                    is_valid=False,
                    reason=result["reason"],
                    expires_at=result.get("expired_at")
                )

            # Token válido
            user_data = result["user"]
            return ValidateActivationTokenResult(
                is_valid=True,
                user=UserForActivation(
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    employee_id=user_data.get("employee_id")  # Opcional
                ),
                expires_at=result["expires_at"]
            )

        except Exception as e:
            return ValidateActivationTokenResult(
                is_valid=False,
                reason=f"Error al validar token: {str(e)}"
            )