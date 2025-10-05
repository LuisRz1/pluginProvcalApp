# app/shared/graphql/context.py
from dataclasses import dataclass
from typing import Optional, TypedDict, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

if TYPE_CHECKING:
    from app.users.domain.user import User
    from app.users.application.ports.user_repository import UserRepository
    from app.users.application.ports.activation_token_repository import ActivationTokenRepository
    from app.users.application.ports.email_service import EmailService
    from app.users.application.ports.auth_service import AuthService


@dataclass
class GraphQLContex(TypedDict):
    """Contexto de GraphQL como TypedDict para Strawberry"""
    request: Request
    session: AsyncSession
    user_repository: "UserRepository"
    token_repository: "ActivationTokenRepository"
    email_service: "EmailService"
    auth_service: "AuthService"
    current_user: Optional["User"] = None

