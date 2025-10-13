from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from contextlib import asynccontextmanager

from app.requests.infrastructure.persistence.shift_swap_repository_impl import PostgreSQLShiftSwapRepository
from app.requests.infrastructure.persistence.time_off_request_repository_impl import PostgreSQLTimeOffRequestRepository
from app.requests.infrastructure.persistence.vacation_balance_repository_impl import PostgreSQLVacationBalanceRepository
from app.requests.infrastructure.persistence.work_schedule_repository_impl import PostgreSQLWorkScheduleRepository
from app.building_blocks.exceptions import AuthenticationException
from app.shared.config.settings import settings
from app.shared.database.connection import init_db, close_db, get_db_session
from app.shared.graphql.schema import schema

# Repositorios
from app.users.infrastructure.persistence.user_repository_impl import PostgreSQLUserRepository
from app.users.infrastructure.persistence.activation_token_repository_impl import PostgreSQLActivationTokenRepository
from app.attendance.infrastructure.persistence.attendance_repository_impl import PostgreSQLAttendanceRepository
from app.attendance.infrastructure.persistence.work_schedule_repository_impl import PostgreSQLWorkScheduleRepository

# Servicios
from app.users.infrastructure.external.email_service import SMTPEmailService
from app.shared.security.auth import JWTAuthService
from app.attendance.infrastructure.services.simple_holiday_service import SimpleHolidayService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Iniciando Sistema de Catering...")
    await init_db()
    print("✅ Base de datos inicializada")
    print(f"📊 GraphQL Playground: http://localhost:8000/graphql")

    yield

    # Shutdown
    print("👋 Cerrando Sistema de Catering...")
    await close_db()
    print("✅ Conexiones cerradas")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Función para crear el contexto de GraphQL
async def get_context(request: Request) -> dict:
    """Crea el contexto de GraphQL con todas las dependencias"""
    authorization = request.headers.get("authorization")

    async with get_db_session() as session:
        # Repositorios existentes
        user_repo = PostgreSQLUserRepository(session)
        token_repo = PostgreSQLActivationTokenRepository(session)
        attendance_repo = PostgreSQLAttendanceRepository(session)
        work_schedule_repo = PostgreSQLWorkScheduleRepository(session)
        time_off_repo = PostgreSQLTimeOffRequestRepository(session)
        vacation_balance_repo = PostgreSQLVacationBalanceRepository(session)
        swap_repo = PostgreSQLShiftSwapRepository(session)
        work_schedule_repo = PostgreSQLWorkScheduleRepository(session)

        # Servicios existentes
        email_service = SMTPEmailService(
            smtp_host=settings.SMTP_HOST,
            smtp_port=settings.SMTP_PORT,
            smtp_username=settings.SMTP_USERNAME,
            smtp_password=settings.SMTP_PASSWORD,
            from_email=settings.SMTP_FROM_EMAIL,
            from_name=settings.SMTP_FROM_NAME
        )

        auth_service = JWTAuthService(
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            access_token_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token_expire_days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )

        holiday_service = SimpleHolidayService()

        current_user = None
        if authorization:
            try:
                token = authorization.replace("Bearer ", "")
                payload = await auth_service.verify_token(token)
                if payload:
                    user_id = payload.get("sub")
                    current_user = await user_repo.find_by_id(user_id)
            except AuthenticationException:
                pass

        # IMPORTANTE: Devolver diccionario, no dataclass
        return {
            "request": request,
            "session": session,
            "user_repository": user_repo,
            "token_repository": token_repo,
            "attendance_repository": attendance_repo,
            "work_schedule_repository": work_schedule_repo,
            "email_service": email_service,
            "auth_service": auth_service,
            "holiday_service": holiday_service,
            "time_off_repository": time_off_repo,
            "vacation_balance_repository": vacation_balance_repo,
            "swap_repository": swap_repo,
            "work_schedule_repository": work_schedule_repo,
            "current_user": current_user
        }


# Configurar GraphQL Router
graphql_app = GraphQLRouter(
    schema=schema,
    context_getter=get_context,
    graphql_ide="apollo-sandbox" if settings.DEBUG else "graphiql"  # GraphiQL solo en desarrollo
)

# Montar GraphQL en /graphql
app.include_router(graphql_app, prefix="/graphql")


# Endpoint de health check
@app.get("/health")
async def health_check():
    """Endpoint para verificar que la API está funcionando"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "graphql": "/graphql",
        "docs": "/docs"
    }

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/users/static"), name="static")

# Rutas para las páginas de activación
@app.get("/activate")
async def activate_page():
    """Página de activación de cuenta"""
    return FileResponse("app/users/templates/activate.html")

@app.get("/activate/success")
async def activate_success_page():
    """Página de éxito tras activación"""
    return FileResponse("app/users/templates/activate_success.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )


