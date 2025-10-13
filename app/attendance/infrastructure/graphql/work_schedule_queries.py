"""Queries GraphQL para horarios"""
from datetime import date
from strawberry.types import Info
import strawberry

from app.attendance.infrastructure.graphql.work_schedule_types import WorkScheduleInfo
from app.attendance.application.use_cases.get_my_schedule import (
    GetMyScheduleUseCase,
    GetMyScheduleCommand
)
from app.building_blocks.exceptions import AuthenticationException


@strawberry.type
class WorkScheduleQueries:

    @strawberry.field
    async def my_schedule(
        self,
        info: Info
    ) -> WorkScheduleInfo:
        """
        Obtiene el horario asignado del usuario actual.
        Requiere autenticación.
        Historia de usuario 2: Revisar horario asignado.
        """
        # Verificar autenticación
        if not info.context.get("current_user"):
            raise AuthenticationException("Debes estar autenticado")

        user = info.context["current_user"]

        # Crear comando
        command = GetMyScheduleCommand(user_id=user.id)

        # Ejecutar caso de uso
        use_case = GetMyScheduleUseCase(
            work_schedule_repository=info.context["work_schedule_repository"]
        )

        result = await use_case.execute(command)

        return WorkScheduleInfo(
            id=result["schedule_id"],
            user_id=user.id,
            shift_type=result["shift_type"],
            start_time=result["start_time"],
            end_time=result["end_time"],
            working_days_names=result["working_days"],
            late_tolerance_minutes=result["late_tolerance_minutes"],
            break_duration_minutes=result["break_duration_minutes"],
            total_hours_per_day=result["total_hours_per_day"],
            is_active=True,
            effective_from=date.fromisoformat(result["effective_from"]),
            effective_until=None,
            notes=result.get("notes")
        )