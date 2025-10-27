# app/shared/graphql/context.py
from dataclasses import dataclass
from typing import Optional, TypedDict, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.menu.application.ports.menu_change_repository import MenuChangeRepository
from app.menu.application.ports.menu_day_repository import MenuDayRepository
from app.menu.application.ports.monthly_menu_repository import MonthlyMenuRepository

if TYPE_CHECKING:
    from app.users.domain.user import User
    from app.users.application.ports.user_repository import UserRepository
    from app.users.application.ports.activation_token_repository import ActivationTokenRepository

    from app.attendance.application.ports.attendance_repository import AttendanceRepository
    from app.attendance.application.ports.holiday_service import HolidayService

    from app.users.application.ports.email_service import EmailService
    from app.users.application.ports.auth_service import AuthService


@dataclass
class GraphQLContex(TypedDict):
    """Contexto de GraphQL como TypedDict para Strawberry"""
    request: Request
    session: AsyncSession

    email_service: "EmailService"
    auth_service: "AuthService"
    holiday_service: "HolidayService"

    user_repository: "UserRepository"
    token_repository: "ActivationTokenRepository"
    attendance_repository: "AttendanceRepository"

    monthly_menu_repository: "MonthlyMenuRepository"
    menu_day_repository: "MenuDayRepository"
    menu_change_repository: "MenuChangeRepository"

    current_user: Optional["User"] = None


