"""Caso de uso: Asignar horario a empleado (Admin)"""
from dataclasses import dataclass
from datetime import time, date
from typing import List, Optional
from app.attendance.domain.work_schedule import WorkSchedule, ShiftType
from app.attendance.application.ports.work_schedule_repository import WorkScheduleRepository
from app.building_blocks.exceptions import DomainException

@dataclass
class AssignWorkScheduleCommand:
    user_id: str
    admin_id: str
    shift_type: str  # "morning", "afternoon", "night", "full_day", "custom"
    start_time: time
    end_time: time
    working_days: List[int]  # [0,1,2,3,4] = Lunes a Viernes
    late_tolerance_minutes: int = 15
    break_duration_minutes: int = 30
    effective_from: date = date.today()
    notes: Optional[str] = None

class AssignWorkScheduleUseCase:
    """
    Caso de uso: Asignar horario de trabajo a un empleado.
    Solo admin puede ejecutar esto.
    """

    def __init__(self, work_schedule_repository: WorkScheduleRepository):
        self.work_schedule_repository = work_schedule_repository

    async def execute(self, command: AssignWorkScheduleCommand) -> dict:
        # 1. Desactivar horario anterior si existe
        current_schedule = await self.work_schedule_repository.find_active_by_user(
            command.user_id
        )

        if current_schedule:
            # Terminar el horario anterior el día anterior al nuevo
            from datetime import timedelta
            end_date = command.effective_from - timedelta(days=1)
            current_schedule.deactivate(end_date)
            await self.work_schedule_repository.save(current_schedule)

        # 2. Crear nuevo horario
        try:
            shift_type = ShiftType(command.shift_type)
        except ValueError:
            raise DomainException(f"Tipo de turno inválido: {command.shift_type}")

        new_schedule = WorkSchedule(
            user_id=command.user_id,
            shift_type=shift_type,
            start_time=command.start_time,
            end_time=command.end_time,
            working_days=command.working_days,
            late_tolerance_minutes=command.late_tolerance_minutes,
            break_duration_minutes=command.break_duration_minutes,
            is_active=True,
            effective_from=command.effective_from,
            created_by=command.admin_id,
            notes=command.notes
        )

        # 3. Guardar
        saved_schedule = await self.work_schedule_repository.save(new_schedule)

        # 4. Respuesta
        return {
            "schedule_id": saved_schedule.id,
            "user_id": saved_schedule.user_id,
            "shift_type": saved_schedule.shift_type.value,
            "start_time": saved_schedule.start_time.isoformat(),
            "end_time": saved_schedule.end_time.isoformat(),
            "working_days": saved_schedule.working_days,
            "effective_from": saved_schedule.effective_from.isoformat(),
            "message": "Horario asignado exitosamente"
        }