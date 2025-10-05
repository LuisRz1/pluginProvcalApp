import strawberry
from strawberry.types import Info
from app.users.infrastructure.graphql.inputs import (
    CreateUserAccountInput,
    ActivateUserAccountInput
)
from app.users.infrastructure.graphql.types import (
    CreateUserAccountResult,
    ActivateUserAccountResult
)
from app.users.application.use_cases.create_user_account import (
    CreateUserAccountUseCase,
    CreateUserAccountCommand
)
from app.users.application.use_cases.activate_user_account import (
    ActivateUserAccountUseCase,
    ActivateUserAccountCommand
)
from app.users.domain.user import UserRole
from app.building_blocks.exceptions import DomainException

@strawberry.type
class UserMutations:

    @strawberry.mutation
    async def create_user_account(
        self,
        info: Info,
        input: CreateUserAccountInput
    ) -> CreateUserAccountResult:
        """
        Crea una cuenta de usuario (solo admin).
        Requiere autenticación y rol de administrador.
        """
        try:
            # Verificar autenticación (implementar según tu sistema)
            # current_user = info.context.current_user
            # if not current_user or current_user.role != UserRole.ADMIN:
            #     return CreateUserAccountResult(
            #         success=False,
            #         message="No tienes permisos para crear usuarios"
            #     )

            # Validar y convertir rol
            try:
                role = UserRole(input.role.lower())
            except ValueError:
                return CreateUserAccountResult(
                    success=False,
                    message=f"Rol inválido: {input.role}"
                )

            # Crear comando
            command = CreateUserAccountCommand(
                employee_id=input.employee_id,
                email=input.email,
                full_name=input.full_name,
                dni=input.dni,
                role=role,
                phone=input.phone,
                address=input.address,
                created_by=None,  # info.context.current_user.id si implementas auth
                activation_base_url=input.activation_base_url
            )

            # Ejecutar caso de uso
            use_case = CreateUserAccountUseCase(
                user_repository=info.context["user_repository"],
                token_repository=info.context["token_repository"],
                email_service=info.context["email_service"]
            )

            result = await use_case.execute(command)

            return CreateUserAccountResult(
                success=True,
                message="Cuenta creada exitosamente. Se ha enviado un email de activación.",
                user_id=result["user_id"],
                employee_id=result["employee_id"],
                email=result["email"],
                activation_token_expires_at=result["activation_token_expires_at"]
            )

        except DomainException as e:
            return CreateUserAccountResult(
                success=False,
                message=str(e)
            )
        except Exception as e:
            # Log error
            return CreateUserAccountResult(
                success=False,
                message=f"Error inesperado: {str(e)}"
            )

    @strawberry.mutation
    async def activate_user_account(
        self,
        info: Info,
        input: ActivateUserAccountInput
    ) -> ActivateUserAccountResult:
        """
        Activa una cuenta de usuario usando el token de activación.
        Esta mutación NO requiere autenticación (es pública).
        """
        try:
            # Crear comando
            command = ActivateUserAccountCommand(
                token=input.token,
                employee_id=input.employee_id,
                password=input.password,
                password_confirmation=input.password_confirmation,
                personal_email=input.personal_email,
                data_processing_consent=input.data_processing_consent
            )

            # Ejecutar caso de uso
            use_case = ActivateUserAccountUseCase(
                user_repository=info.context["user_repository"],
                token_repository=info.context["token_repository"],
                email_service=info.context["email_service"]
            )

            result = await use_case.execute(command)

            return ActivateUserAccountResult(
                success=True,
                message="¡Cuenta activada exitosamente! Ya puedes iniciar sesión.",
                user_id=result["user_id"],
                email=result["email"]
            )

        except DomainException as e:
            return ActivateUserAccountResult(
                success=False,
                message=str(e)
            )
        except Exception as e:
            # Log error
            return ActivateUserAccountResult(
                success=False,
                message=f"Error al activar la cuenta: {str(e)}"
            )
