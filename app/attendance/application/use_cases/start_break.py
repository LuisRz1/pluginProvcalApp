"""Caso de uso: Iniciar descanso"""
from dataclasses import dataclass
from datetime import datetime, timezone
from app.attendance.domain.geolocation import Geolocation
from app.attendance.application.ports.attendance_repository import AttendanceRepository
from app.building_blocks.exceptions import DomainException

@dataclass
class StartBreakCommand:
    user_id: str
    latitude: float
    longitude: float
    accuracy: float = 10.0

class StartBreakUseCase:
    """
    Caso de uso: Iniciar período de descanso.
    """

    def __init__(self, attendance_repository: AttendanceRepository):
        self.attendance_repository = attendance_repository

    async def execute(self, command: StartBreakCommand) -> dict:
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

        # 3. Iniciar descanso
        break_period = attendance.start_break(location)

        # 4. Guardar
        await self.attendance_repository.save(attendance)

        # 5. Respuesta
        return {
            "break_id": break_period.id,
            "start_time": break_period.start_time.isoformat(),
            "allowed_duration_minutes": break_period.allowed_duration_minutes,
            "message": f"Descanso iniciado. Duración permitida: {break_period.allowed_duration_minutes} minutos"
        }