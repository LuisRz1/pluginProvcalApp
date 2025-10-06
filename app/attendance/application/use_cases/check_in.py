"""Caso de uso: Registrar entrada"""
from dataclasses import dataclass
from datetime import datetime, timezone
from app.attendance.domain.attendance import Attendance
from app.attendance.domain.geolocation import Geolocation
from app.attendance.application.ports.attendance_repository import AttendanceRepository
from app.attendance.application.ports.holiday_service import HolidayService
from app.building_blocks.exceptions import DomainException

@dataclass
class CheckInCommand:
    user_id: str
    latitude: float
    longitude: float
    accuracy: float = 10.0
    # Configuración del lugar de trabajo (esto debería venir de configuración)
    workplace_latitude: float = -8.1116778  # Ejemplo: Trujillo
    workplace_longitude: float = -79.0287578
    workplace_radius_meters: float = 100.0

class CheckInUseCase:
    """
    Caso de uso: Registrar entrada.

    Escenarios:
    1. Entrada exitosa (en horario)
    2. Entrada tardía (fuera de horario)
    """

    def __init__(
        self,
        attendance_repository: AttendanceRepository,
        holiday_service: HolidayService
    ):
        self.attendance_repository = attendance_repository
        self.holiday_service = holiday_service

    async def execute(self, command: CheckInCommand) -> dict:
        # 1. Verificar si tiene asistencias pendientes de regularización
        has_pending = await self.attendance_repository.has_pending_regularization(
            command.user_id
        )

        if has_pending:
            raise DomainException(
                "Tienes asistencias pendientes de regularización. "
                "Contacta con RRHH antes de registrar nueva entrada."
            )

        # 2. Verificar si ya registró entrada hoy
        today = datetime.now(timezone.utc).date()
        existing = await self.attendance_repository.find_by_user_and_date(
            command.user_id, today
        )

        if existing and existing.check_in_time:
            raise DomainException("Ya registraste tu entrada hoy")

        # 3. Crear ubicación
        location = Geolocation(
            latitude=command.latitude,
            longitude=command.longitude,
            accuracy=command.accuracy
        )

        workplace_location = Geolocation(
            latitude=command.workplace_latitude,
            longitude=command.workplace_longitude
        )

        # 4. Verificar si es día festivo
        is_holiday = await self.holiday_service.is_holiday(today)

        # 5. Crear o actualizar asistencia
        if existing:
            attendance = existing
        else:
            attendance = Attendance(
                user_id=command.user_id,
                date=datetime.now(timezone.utc),
                workplace_location=workplace_location,
                workplace_radius_meters=command.workplace_radius_meters
            )

        # 6. Registrar entrada
        attendance.check_in(location, is_holiday)

        # 7. Guardar
        saved_attendance = await self.attendance_repository.save(attendance)

        # 8. Preparar respuesta
        return {
            "attendance_id": saved_attendance.id,
            "check_in_time": saved_attendance.check_in_time.isoformat(),
            "is_late": saved_attendance.is_late,
            "late_minutes": saved_attendance.late_minutes if saved_attendance.is_late else 0,
            "is_holiday": is_holiday,
            "message": self._get_check_in_message(saved_attendance, is_holiday)
        }

    def _get_check_in_message(self, attendance: Attendance, is_holiday: bool) -> str:
        if is_holiday:
            return f"Entrada registrada en día festivo a las {attendance.check_in_time.strftime('%H:%M')}"
        elif attendance.is_late:
            return f"Entrada tardía registrada ({attendance.late_minutes} minutos de retraso)"
        else:
            return f"Entrada registrada exitosamente a las {attendance.check_in_time.strftime('%H:%M')}"
