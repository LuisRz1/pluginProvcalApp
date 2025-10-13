"""Caso de uso: Registrar entrada"""
from dataclasses import dataclass
from datetime import datetime, timezone, date
from app.attendance.domain.attendance import Attendance
from app.attendance.domain.geolocation import Geolocation
from app.attendance.application.ports.attendance_repository import AttendanceRepository
from app.attendance.application.ports.holiday_service import HolidayService
from app.attendance.application.ports.work_schedule_repository import WorkScheduleRepository
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
        holiday_service: HolidayService,
        work_schedule_repository: WorkScheduleRepository
    ):
        self.attendance_repository = attendance_repository
        self.holiday_service = holiday_service
        self.work_schedule_repository = work_schedule_repository

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
        today = date.today()
        existing = await self.attendance_repository.find_by_user_and_date(
            command.user_id, today
        )

        if existing and existing.check_in_time:
            raise DomainException("Ya registraste tu entrada hoy")

        # 3. Obtener horario del empleado
        schedule = await self.work_schedule_repository.find_by_user_and_date(
            command.user_id, today
        )

        if not schedule:
            raise DomainException(
                "No tienes horario asignado. Contacta con RRHH para que te asignen un horario."
            )

        # 4. Verificar que sea día laboral
        if not schedule.is_working_day(today):
            day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            raise DomainException(
                f"Hoy {day_names[today.weekday()]} no es tu día laboral según tu horario"
            )

        # 5. Crear ubicación
        location = Geolocation(
            latitude=command.latitude,
            longitude=command.longitude,
            accuracy=command.accuracy
        )

        workplace_location = Geolocation(
            latitude=command.workplace_latitude,
            longitude=command.workplace_longitude
        )

        # 6. Verificar si es día festivo
        is_holiday = await self.holiday_service.is_holiday(today)

        # 7. Crear o actualizar asistencia con horario del empleado
        if existing:
            attendance = existing
        else:
            attendance = Attendance(
                user_id=command.user_id,
                date=datetime.now(timezone.utc),
                scheduled_start_time=schedule.start_time,
                scheduled_end_time=schedule.end_time,
                late_tolerance_minutes=schedule.late_tolerance_minutes,
                workplace_location=workplace_location,
                workplace_radius_meters=command.workplace_radius_meters
            )

        # 8. Registrar entrada
        attendance.check_in(location, is_holiday)

        # 9. Guardar
        saved_attendance = await self.attendance_repository.save(attendance)

        # 10. Preparar respuesta
        return {
            "attendance_id": saved_attendance.id,
            "check_in_time": saved_attendance.check_in_time.isoformat(),
            "scheduled_start_time": saved_attendance.scheduled_start_time.isoformat(),
            "is_late": saved_attendance.is_late,
            "late_minutes": saved_attendance.late_minutes if saved_attendance.is_late else 0,
            "is_holiday": is_holiday,
            "message": self._get_check_in_message(saved_attendance, is_holiday, schedule)
        }

    def _get_check_in_message(self, attendance: Attendance, is_holiday: bool, schedule) -> str:
        check_in_str = attendance.check_in_time.strftime('%H:%M')
        scheduled_str = attendance.scheduled_start_time.strftime('%H:%M')

        if is_holiday:
            return f"Entrada registrada en día festivo a las {check_in_str}"
        elif attendance.is_late:
            return f"Entrada tardía a las {check_in_str} ({attendance.late_minutes} minutos de retraso). Hora programada: {scheduled_str}"
        else:
            return f"Entrada registrada a las {check_in_str}. ¡Puntual!"