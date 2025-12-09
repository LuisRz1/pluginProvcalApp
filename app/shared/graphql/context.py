# app/shared/graphql/context.py
from dataclasses import dataclass
from typing import Optional, TypedDict, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

# MENU
from app.menu.application.ports.monthly_menu_repository import MonthlyMenuRepository
from app.menu.application.ports.weekly_menu_repository import WeeklyMenuRepository
from app.menu.application.ports.daily_menu_repository import DailyMenuRepository
from app.menu.application.ports.meal_repository import MealRepository
from app.menu.application.ports.meal_component_repository import MealComponentRepository
from app.menu.application.ports.menu_change_repository import MenuChangeRepository
from app.menu.application.ports.component_type_repository import ComponentTypeRepository

# REQUESTS
from app.requests.application.ports.shift_swap_repository import ShiftSwapRepository
from app.requests.application.ports.time_off_request_repository import (
    TimeOffRequestRepository,
)
from app.requests.application.ports.vacation_balance_repository import (
    VacationBalanceRepository,
)
from app.requests.application.ports.work_schedule_repository import (
    WorkScheduleRepository,
)

# SANITARY (nuevo módulo de sanidad)
from app.sanitary.application.ports.sanitary_policy_repository import (
    SanitaryPolicyRepository,
)
from app.sanitary.application.ports.incident_type_repository import (
    IncidentTypeRepository,
)
from app.sanitary.application.ports.sanitary_review_repository import (
    SanitaryReviewRepository,
)
from app.sanitary.application.ports.sanitary_company_repository import (
    SanitaryCompanyRepository,
)

if TYPE_CHECKING:
    from app.users.domain.user import User
    from app.users.application.ports.user_repository import UserRepository
    from app.users.application.ports.activation_token_repository import (
        ActivationTokenRepository,
    )

    from app.attendance.application.ports.attendance_repository import (
        AttendanceRepository,
    )
    from app.attendance.application.ports.holiday_service import HolidayService

    from app.users.application.ports.email_service import EmailService
    from app.users.application.ports.auth_service import AuthService


@dataclass
class GraphQLContex(TypedDict):
    """Contexto de GraphQL como TypedDict para Strawberry"""

    request: Request
    session: AsyncSession

    # Usuarios / Auth / Attendance
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

    # Menú
    monthly_menu_repository: "MonthlyMenuRepository"
    weekly_menu_repository: "WeeklyMenuRepository"
    daily_menu_repository: "DailyMenuRepository"
    meal_repository: "MealRepository"
    meal_component_repository: "MealComponentRepository"
    menu_change_repository: "MenuChangeRepository"
    component_type_repository: "ComponentTypeRepository"

    # Sanidad (nuevo)
    sanitary_policy_repository: "SanitaryPolicyRepository"
    incident_type_repository: "IncidentTypeRepository"
    sanitary_review_repository: "SanitaryReviewRepository"
    sanitary_company_repository: "SanitaryCompanyRepository"

    current_user: Optional["User"] = None
