"""Caso de uso: Registrar salida"""
from dataclasses import dataclass
from datetime import datetime, timezone
from app.attendance.domain.geolocation import Geolocation
from app.attendance.domain.attendance import Attendance
from app.attendance.application.ports.attendance_repository import AttendanceRepository
from app.building_blocks.exceptions import DomainException

@dataclass
class CheckOutCommand:
    user_id: str
    latitude: float
    longitude: float
    accuracy: float = 10.0

class CheckOutUseCase:
    """
    Caso de uso: Registrar salida.

    Escenarios:
    - Salida normal
    - Salida sin haber marcado descansos (permitido pero registrado)
    """

    def __init__(self, attendance_repository: AttendanceRepository):
        self.attendance_repository = attendance_repository

    async def execute(self, command: CheckOutCommand) -> dict:
        # 1. Obtener asistencia del día
        #today = date.today()
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

        # 3. Verificar si tiene descansos incompletos
        no_breaks = len(attendance.break_periods) == 0

        # 4. Registrar salida
        attendance.check_out(location)

        # 5. Guardar
        await self.attendance_repository.save(attendance)

        # 6. Calcular horas trabajadas
        work_hours = attendance.get_total_work_hours()

        # 7. Respuesta
        return {
            "attendance_id": attendance.id,
            "check_out_time": attendance.check_out_time.isoformat(),
            "total_work_hours": round(work_hours, 2),
            "no_breaks_registered": no_breaks,
            "message": self._get_checkout_message(attendance, no_breaks)
        }

    def _get_checkout_message(self, attendance: Attendance, no_breaks: bool) -> str:
        hours = attendance.get_total_work_hours()
        msg = f"Salida registrada. Total trabajado: {hours:.2f} horas"

        if no_breaks:
            msg += ". ADVERTENCIA: No registraste descansos durante esta jornada"

        return msg