"""
Comando CLI para crear cuentas de usuario.
Uso: python -m app.cli.commands.create_user
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from app.users.domain.user_role import UserRole
from app.users.application.use_cases.create_user_account import (
    CreateUserAccountUseCase,
    CreateUserAccountCommand
)
from app.shared.database.connection import get_db_session
from app.users.infrastructure.persistence.user_repository_impl import PostgreSQLUserRepository
from app.users.infrastructure.persistence.activation_token_repository_impl import PostgreSQLActivationTokenRepository
from app.users.infrastructure.external.email_service import SMTPEmailService
from app.shared.config.settings import settings


async def create_user_interactive():
    """Crea un usuario de forma interactiva"""
    print("=" * 60)
    print("CREAR CUENTA DE USUARIO - Sistema de Catering")
    print("=" * 60)
    print()

    # Recopilar información
    employee_id = input("ID de Empleado: ").strip()
    email = input("Email corporativo: ").strip()
    full_name = input("Nombre completo: ").strip()
    dni = input("DNI: ").strip()

    print("\nRoles disponibles:")
    for i, role in enumerate(UserRole, 1):
        print(f"  {i}. {role.value}")

    role_choice = int(input("\nSelecciona el rol (número): ").strip())
    role = list(UserRole)[role_choice - 1]

    phone = input("Teléfono (opcional): ").strip() or None
    address = input("Dirección (opcional): ").strip() or None

    activation_base_url = input(
        "URL base para activación [https://app.catering.com]: "
    ).strip() or "https://app.catering.com"

    print("\n" + "-" * 60)
    print("RESUMEN:")
    print(f"  Employee ID: {employee_id}")
    print(f"  Email: {email}")
    print(f"  Nombre: {full_name}")
    print(f"  DNI: {dni}")
    print(f"  Rol: {role.value}")
    print(f"  Teléfono: {phone or 'N/A'}")
    print(f"  Dirección: {address or 'N/A'}")
    print("-" * 60)

    confirm = input("\n¿Crear este usuario? (s/n): ").strip().lower()

    if confirm != 's':
        print("Operación cancelada.")
        return

    # Crear usuario
    print("\nCreando usuario...")

    try:
        async with get_db_session() as session:
            # Inicializar repositorios
            user_repo = PostgreSQLUserRepository(session)
            token_repo = PostgreSQLActivationTokenRepository(session)

            # Inicializar servicio de email
            email_service = SMTPEmailService(
                smtp_host=settings.SMTP_HOST,
                smtp_port=settings.SMTP_PORT,
                smtp_username=settings.SMTP_USERNAME,
                smtp_password=settings.SMTP_PASSWORD,
                from_email=settings.SMTP_FROM_EMAIL,
                from_name=settings.SMTP_FROM_NAME
            )

            # Crear comando
            command = CreateUserAccountCommand(
                employee_id=employee_id,
                email=email,
                full_name=full_name,
                dni=dni,
                role=role,
                phone=phone,
                address=address,
                created_by=None,  # CLI command
                activation_base_url=activation_base_url
            )

            # Ejecutar caso de uso
            use_case = CreateUserAccountUseCase(
                user_repository=user_repo,
                token_repository=token_repo,
                email_service=email_service
            )

            result = await use_case.execute(command)

            print("\n" + "=" * 60)
            print("USUARIO CREADO EXITOSAMENTE")
            print("=" * 60)
            print(f"  User ID: {result['user_id']}")
            print(f"  Employee ID: {result['employee_id']}")
            print(f"  Email: {result['email']}")
            print(f"  Estado: {result['status']}")
            print(f"  Token expira: {result['activation_token_expires_at']}")
            print("\nEmail de activación enviado correctamente.")
            print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


async def create_user_from_args(args):
    """Crea un usuario desde argumentos de línea de comandos"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Crear cuenta de usuario en el sistema'
    )
    parser.add_argument('--employee-id', required=True, help='ID del empleado')
    parser.add_argument('--email', required=True, help='Email corporativo')
    parser.add_argument('--full-name', required=True, help='Nombre completo')
    parser.add_argument('--dni', required=True, help='DNI')
    parser.add_argument('--role', required=True,
                       choices=[r.value for r in UserRole],
                       help='Rol del usuario')
    parser.add_argument('--phone', help='Teléfono (opcional)')
    parser.add_argument('--address', help='Dirección (opcional)')
    parser.add_argument('--activation-url',
                       default='https://app.catering.com',
                       help='URL base para activación')

    parsed_args = parser.parse_args(args)

    try:
        role = UserRole(parsed_args.role)

        async with get_db_session() as session:
            user_repo = PostgreSQLUserRepository(session)
            token_repo = PostgreSQLActivationTokenRepository(session)

            email_service = SMTPEmailService(
                smtp_host=settings.SMTP_HOST,
                smtp_port=settings.SMTP_PORT,
                smtp_username=settings.SMTP_USERNAME,
                smtp_password=settings.SMTP_PASSWORD,
                from_email=settings.SMTP_FROM_EMAIL,
                from_name=settings.SMTP_FROM_NAME
            )

            command = CreateUserAccountCommand(
                employee_id=parsed_args.employee_id,
                email=parsed_args.email,
                full_name=parsed_args.full_name,
                dni=parsed_args.dni,
                role=role,
                phone=parsed_args.phone,
                address=parsed_args.address,
                created_by=None,
                activation_base_url=parsed_args.activation_url
            )

            use_case = CreateUserAccountUseCase(
                user_repository=user_repo,
                token_repository=token_repo,
                email_service=email_service
            )

            result = await use_case.execute(command)

            print(f"✅ Usuario creado: {result['user_id']}")
            print(f"   Email: {result['email']}")
            print(f"   Token expira: {result['activation_token_expires_at']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Modo con argumentos
        asyncio.run(create_user_from_args(sys.argv[1:]))
    else:
        # Modo interactivo
        asyncio.run(create_user_interactive())


# Ejemplo de uso:
# Interactivo:
# python -m app.cli.commands.create_user

# Con argumentos:
# python -m app.cli.commands.create_user \
#   --employee-id EMP001 \
#   --email juan.perez@catering.com \
#   --full-name "Juan Pérez" \
#   --dni 12345678 \
#   --role employee \
#   --phone 987654321 \
#   --activation-url https://app.catering.com