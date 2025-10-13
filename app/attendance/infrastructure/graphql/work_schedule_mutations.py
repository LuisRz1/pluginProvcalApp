"""Mutations GraphQL para horarios"""
from strawberry.types import Info
import strawberry

from app.attendance.infrastructure.graphql.work_schedule_inputs import AssignWorkScheduleInput
from app.attendance.infrastructure.graphql.work_schedule_types import (
    AssignScheduleResponse,
    WorkScheduleInfo
)
from app.attendance.application.use_cases.assign_work_schedule import (
    AssignWorkScheduleUseCase,
    AssignWorkScheduleCommand
)
from app.building_blocks.exceptions import DomainException, AuthenticationException
from app.users.domain.user_role import UserRole


@strawberry.type
class WorkScheduleMutations:

    @strawberry.mutation
    async def assign_work_schedule(
        self,
        info: Info,
        input: AssignWorkScheduleInput
    ) -> AssignScheduleResponse:
        """
        Asigna un horario de trabajo a un empleado.
        Solo admin puede ejecutar esto.
        """
        try:
            # Verificar autenticación
            if not info.context.get("current_user"):
                raise AuthenticationException("Debes estar autenticado")

            admin = info.context["current_user"]

            # Verificar que sea admin
            if admin.role != UserRole.ADMIN:
                raise AuthenticationException(
                    "Solo administradores pueden asignar horarios"
                )

            # Crear comando
            command = AssignWorkScheduleCommand(
                user_id=input.user_id,
                admin_id=admin.id,
                shift_type=input.shift_type,
                start_time=input.start_time,
                end_time=input.end_time,
                working_days=input.working_days,
                late_tolerance_minutes=input.late_tolerance_minutes,
                break_duration_minutes=input.break_duration_minutes,
                effective_from=input.effective_from,
                notes=input.notes
            )

            # Ejecutar caso de uso
            use_case = AssignWorkScheduleUseCase(
                work_schedule_repository=info.context["work_schedule_repository"]
            )

            result = await use_case.execute(command)

            # Mapear días
            day_names = {
                0: "Lunes", 1: "Martes", 2: "Miércoles",
                3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
            }
            working_days_names = [
                day_names[day] for day in sorted(input.working_days)
            ]

            schedule_info = WorkScheduleInfo(
                id=result["schedule_id"],
                user_id=result["user_id"],
                shift_type=result["shift_type"],
                start_time=result["start_time"],
                end_time=result["end_time"],
                working_days_names=working_days_names,
                late_tolerance_minutes=input.late_tolerance_minutes,
                break_duration_minutes=input.break_duration_minutes,
                total_hours_per_day=0.0,  # Se calculará después
                is_active=True,
                effective_from=input.effective_from,
                effective_until=None,
                notes=input.notes
            )

            return AssignScheduleResponse(
                success=True,
                message=result["message"],
                schedule=schedule_info
            )

        except (DomainException, AuthenticationException) as e:
            return AssignScheduleResponse(
                success=False,
                message=str(e),
                schedule=None
            )