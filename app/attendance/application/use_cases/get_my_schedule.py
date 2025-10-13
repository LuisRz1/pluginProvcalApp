"""Caso de uso: Ver mi horario asignado"""
from dataclasses import dataclass
from app.attendance.application.ports.work_schedule_repository import WorkScheduleRepository
from app.building_blocks.exceptions import DomainException


@dataclass
class GetMyScheduleCommand:
    user_id: str

class GetMyScheduleUseCase:
    """
    Caso de uso: Obtener el horario actual del empleado.
    Historia de usuario 2: El empleado puede revisar su horario asignado.
    """

    def __init__(self, work_schedule_repository: WorkScheduleRepository):
        self.work_schedule_repository = work_schedule_repository

    async def execute(self, command: GetMyScheduleCommand) -> dict:
        schedule = await self.work_schedule_repository.find_active_by_user(
            command.user_id
        )

        if not schedule:
            raise DomainException("No tienes horario asignado. Contacta con RRHH")

        # Mapear días a nombres
        day_names = {
            0: "Lunes", 1: "Martes", 2: "Miércoles",
            3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
        }

        working_days_names = [day_names[day] for day in sorted(schedule.working_days)]

        return {
            "schedule_id": schedule.id,
            "shift_type": schedule.shift_type.value,
            "start_time": schedule.start_time.strftime("%H:%M"),
            "end_time": schedule.end_time.strftime("%H:%M"),
            "working_days": working_days_names,
            "late_tolerance_minutes": schedule.late_tolerance_minutes,
            "break_duration_minutes": schedule.break_duration_minutes,
            "total_hours_per_day": round(schedule.get_total_hours_per_day(), 2),
            "effective_from": schedule.effective_from.isoformat(),
            "notes": schedule.notes
        }