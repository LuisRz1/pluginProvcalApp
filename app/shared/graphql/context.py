# app/shared/graphql/context.py
from dataclasses import dataclass
from typing import Optional, TypedDict, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.menu.application.ports.menu_change_repository import MenuChangeRepository
from app.menu.application.ports.menu_day_repository import MenuDayRepository
from app.menu.application.ports.monthly_menu_repository import MonthlyMenuRepository

from app.requests.application.ports.shift_swap_repository import ShiftSwapRepository
from app.requests.application.ports.time_off_request_repository import TimeOffRequestRepository
from app.requests.application.ports.vacation_balance_repository import VacationBalanceRepository
from app.requests.application.ports.work_schedule_repository import WorkScheduleRepository

if TYPE_CHECKING:
    from app.users.domain.user import User
    from app.users.application.ports.user_repository import UserRepository
    from app.users.application.ports.activation_token_repository import ActivationTokenRepository

    from app.attendance.application.ports.attendance_repository import AttendanceRepository
    from app.attendance.application.ports.holiday_service import HolidayService

    from app.users.application.ports.email_service import EmailService
    from app.users.application.ports.auth_service import AuthService
    from app.attendance.application.ports.holiday_service import HolidayService


@dataclass
class GraphQLContex(TypedDict):
    """Contexto de GraphQL como TypedDict para Strawberry"""
    request: Request
    session: AsyncSession
    user_repository: "UserRepository"
    token_repository: "ActivationTokenRepository"
    attendance_repository: "AttendanceRepository"

    time_off_repository: "TimeOffRequestRepository"
    vacation_balance_repository: "VacationBalanceRepository"
    swap_repository: "ShiftSwapRepository"
    work_schedule_repository: "WorkScheduleRepository"

    email_service: "EmailService"
    auth_service: "AuthService"
    holiday_service: "HolidayService"

    monthly_menu_repository: "MonthlyMenuRepository"
    menu_day_repository: "MenuDayRepository"
    menu_change_repository: "MenuChangeRepository"

    current_user: Optional["User"] = None


