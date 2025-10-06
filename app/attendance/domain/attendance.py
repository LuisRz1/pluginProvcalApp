"""Entidad principal de asistencia"""
from dataclasses import dataclass, field
from datetime import datetime, time, timezone
from typing import Optional, List
from app.attendance.domain.attendance_status import AttendanceStatus, AttendanceType, BreakStatus
from app.attendance.domain.geolocation import Geolocation
from app.attendance.domain.break_period import BreakPeriod
from app.building_blocks.exceptions import DomainException

@dataclass
class Attendance:
    """
    Entidad de asistencia laboral.
    Representa una jornada de trabajo de un empleado.
    """
    id: Optional[str] = None
    user_id: str = ""
    date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Horarios
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    scheduled_start_time: time = time(9, 0)  # 9:00 AM por defecto
    scheduled_end_time: time = time(18, 0)  # 6:00 PM por defecto

    # Estado
    status: AttendanceStatus = AttendanceStatus.IN_PROGRESS
    type: AttendanceType = AttendanceType.REGULAR

    # Geolocalización
    check_in_location: Optional[Geolocation] = None
    check_out_location: Optional[Geolocation] = None
    workplace_location: Optional[Geolocation] = None
    workplace_radius_meters: float = 100.0

    # Tardanzas y ajustes
    is_late: bool = False
    late_minutes: int = 0
    requires_regularization: bool = False
    regularization_notes: Optional[str] = None
    regularized_by: Optional[str] = None  # ID del admin
    regularized_at: Optional[datetime] = None

    # Descansos
    break_periods: List[BreakPeriod] = field(default_factory=list)

    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def check_in(self, location: Geolocation, is_holiday: bool = False) -> None:
        """
        Registra la entrada del empleado.

        Args:
            location: Ubicación del registro
            is_holiday: Si es día festivo
        """
        if self.check_in_time:
            raise DomainException("Ya se registró la entrada para esta jornada")

        # Validar ubicación
        if self.workplace_location and not location.is_within_radius(
            self.workplace_location, self.workplace_radius_meters
        ):
            raise DomainException(
                "Debes estar en el área de trabajo para registrar tu entrada"
            )

        now = datetime.now(timezone.utc)
        self.check_in_time = now
        self.check_in_location = location
        self.status = AttendanceStatus.IN_PROGRESS

        # Marcar si es día festivo
        if is_holiday:
            self.type = AttendanceType.HOLIDAY

        # Calcular tardanza
        self._calculate_lateness()

        self.updated_at = now

    def _calculate_lateness(self) -> None:
        """Calcula si llegó tarde y cuántos minutos"""
        if not self.check_in_time:
            return

        # Combinar fecha con hora programada
        scheduled_datetime = datetime.combine(
            self.date.date(),
            self.scheduled_start_time,
            tzinfo=timezone.utc
        )

        if self.check_in_time > scheduled_datetime:
            self.is_late = True
            delta = self.check_in_time - scheduled_datetime
            self.late_minutes = int(delta.total_seconds() / 60)
        else:
            self.is_late = False
            self.late_minutes = 0

    def start_break(self, location: Geolocation) -> BreakPeriod:
        """
        Inicia un período de descanso.

        Args:
            location: Ubicación del registro

        Returns:
            El período de descanso creado
        """
        if not self.check_in_time:
            raise DomainException("Debes registrar tu entrada primero")

        if self.check_out_time:
            raise DomainException("Ya registraste tu salida")

        if self.status == AttendanceStatus.ON_BREAK:
            raise DomainException("Ya estás en descanso")

        # Crear nuevo período de descanso
        break_period = BreakPeriod(
            attendance_id=self.id,
            allowed_duration_minutes=30
        )
        break_period.start_break(location)

        self.break_periods.append(break_period)
        self.status = AttendanceStatus.ON_BREAK
        self.updated_at = datetime.now(timezone.utc)

        return break_period

    def end_break(self, location: Geolocation) -> None:
        """
        Finaliza el período de descanso actual.

        Args:
            location: Ubicación del registro
        """
        if self.status != AttendanceStatus.ON_BREAK:
            raise DomainException("No estás en descanso")

        # Obtener el último descanso
        current_break = self._get_current_break()
        if not current_break:
            raise DomainException("No hay descanso activo")

        # Finalizar descanso
        current_break.end_break(location, self.workplace_location, self.workplace_radius_meters)

        self.status = AttendanceStatus.IN_PROGRESS
        self.updated_at = datetime.now(timezone.utc)

    def check_out(self, location: Geolocation) -> None:
        """
        Registra la salida del empleado.

        Args:
            location: Ubicación del registro
        """
        if not self.check_in_time:
            raise DomainException("Debes registrar tu entrada primero")

        if self.check_out_time:
            raise DomainException("Ya registraste tu salida")

        if self.status == AttendanceStatus.ON_BREAK:
            raise DomainException(
                "No puedes marcar salida mientras estás en descanso"
            )

        # Validar ubicación
        if self.workplace_location and not location.is_within_radius(
            self.workplace_location, self.workplace_radius_meters
        ):
            raise DomainException(
                "Debes estar en el área de trabajo para registrar tu salida"
            )

        now = datetime.now(timezone.utc)
        self.check_out_time = now
        self.check_out_location = location
        self.status = AttendanceStatus.COMPLETED
        self.updated_at = now

    def _get_current_break(self) -> Optional[BreakPeriod]:
        """Obtiene el descanso activo actual"""
        for break_period in self.break_periods:
            if break_period.status == BreakStatus.IN_PROGRESS:
                return break_period
        return None

    def regularize(self, admin_id: str, notes: str, adjusted_check_in: Optional[datetime] = None) -> None:
        """
        Regulariza la asistencia (solo admin).

        Args:
            admin_id: ID del administrador
            notes: Notas de regularización
            adjusted_check_in: Hora de entrada ajustada (opcional)
        """
        if adjusted_check_in:
            self.check_in_time = adjusted_check_in
            self._calculate_lateness()

        self.requires_regularization = False
        self.regularization_notes = notes
        self.regularized_by = admin_id
        self.regularized_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def get_total_work_hours(self) -> Optional[float]:
        """Calcula las horas totales trabajadas (sin contar descansos)"""
        if not self.check_in_time:
            return None

        end_time = self.check_out_time or datetime.now(timezone.utc)
        total_seconds = (end_time - self.check_in_time).total_seconds()

        # Restar tiempo de descansos
        break_seconds = sum(
            (bp.get_duration_minutes() or 0) * 60
            for bp in self.break_periods
            if bp.status != BreakStatus.IN_PROGRESS
        )

        work_seconds = total_seconds - break_seconds
        return work_seconds / 3600  # Convertir a horas

    def has_incomplete_breaks(self) -> bool:
        """Verifica si hay descansos sin finalizar"""
        return any(
            bp.status == BreakStatus.IN_PROGRESS
            for bp in self.break_periods
        )

    def mark_as_requiring_regularization(self, reason: str) -> None:
        """Marca la asistencia como que requiere regularización"""
        self.requires_regularization = True
        self.status = AttendanceStatus.PENDING_REGULARIZATION
        self.regularization_notes = reason
        self.updated_at = datetime.now(timezone.utc)