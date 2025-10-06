"""Caso de uso: Finalizar descanso"""
from dataclasses import dataclass
from datetime import datetime, timezone
from app.attendance.domain.geolocation import Geolocation
from app.attendance.application.ports.attendance_repository import AttendanceRepository
from app.building_blocks.exceptions import DomainException

@dataclass
class EndBreakCommand:
    user_id: str
    latitude: float
    longitude: float
    accuracy: float = 10.0

class EndBreakUseCase:
    """
    Caso de uso: Finalizar período de descanso.
    """

    def __init__(self, attendance_repository: AttendanceRepository):
        self.attendance_repository = attendance_repository

    async def execute(self, command: EndBreakCommand) -> dict:
        # 1. Obtener asistencia del día
        today = datetime.now(timezone.utc).date()
        attendance = await self.attendance_repository.find_by_user_and_date(
            command.user_id, today
        )

        if not attendance:
            raise DomainException("No has registrado tu entrada hoy")

        # 2. Crear ubicación
        location = Geolocation(
            latitude=command.latitude,
            longitude=command.longitude,
            accuracy=command.accuracy
        )

        # 3. Finalizar descanso
        attendance.end_break(location)

        # 4. Guardar
        await self.attendance_repository.save(attendance)

        # 5. Obtener información del descanso
        last_break = attendance.break_periods[-1]
        duration = last_break.get_duration_minutes()

        # 6. Respuesta
        return {
            "end_time": last_break.end_time.isoformat(),
            "duration_minutes": duration,
            "is_exceeded": last_break.is_exceeded(),
            "message": self._get_end_break_message(last_break)
        }

    def _get_end_break_message(self, break_period) -> str:
        duration = break_period.get_duration_minutes()
        if break_period.is_exceeded():
            excess = duration - break_period.allowed_duration_minutes
            return f"Descanso finalizado. Excediste {excess} minutos del tiempo permitido"
        return f"Descanso finalizado. Duración: {duration} minutos"