"""Entidad para períodos de descanso"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from app.attendance.domain.attendance_status import BreakStatus
from app.attendance.domain.geolocation import Geolocation
from app.building_blocks.exceptions import DomainException

@dataclass
class BreakPeriod:
    """Período de descanso dentro de una jornada"""
    id: Optional[str] = None
    attendance_id: str = ""

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: BreakStatus = BreakStatus.IN_PROGRESS

    # Geolocalización
    start_location: Optional[Geolocation] = None
    end_location: Optional[Geolocation] = None

    # Configuración
    allowed_duration_minutes: int = 30

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def start_break(self, location: Geolocation) -> None:
        """Inicia el período de descanso"""
        if self.start_time:
            raise DomainException("El descanso ya fue iniciado")

        self.start_time = datetime.now(timezone.utc)
        self.start_location = location
        self.status = BreakStatus.IN_PROGRESS

    def end_break(self, location: Geolocation, workplace_location: Geolocation, radius_meters: float = 100) -> None:
        """
        Finaliza el período de descanso.

        Args:
            location: Ubicación al finalizar
            workplace_location: Ubicación del lugar de trabajo
            radius_meters: Radio permitido del lugar de trabajo
        """
        if not self.start_time:
            raise DomainException("El descanso no ha sido iniciado")

        if self.end_time:
            raise DomainException("El descanso ya fue finalizado")

        # Validar ubicación
        if not location.is_within_radius(workplace_location, radius_meters):
            raise DomainException(
                "Debes estar en el área de trabajo para finalizar el descanso"
            )

        self.end_time = datetime.now(timezone.utc)
        self.end_location = location

        # Verificar si excedió el tiempo permitido
        duration = self.get_duration_minutes()
        if duration > self.allowed_duration_minutes:
            self.status = BreakStatus.EXCEEDED
        else:
            self.status = BreakStatus.COMPLETED

    def get_duration_minutes(self) -> Optional[int]:
        """Calcula la duración del descanso en minutos"""
        if not self.start_time:
            return None

        end = self.end_time or datetime.now(timezone.utc)
        delta = end - self.start_time
        return int(delta.total_seconds() / 60)

    def is_exceeded(self) -> bool:
        """Verifica si el descanso excedió el tiempo permitido"""
        duration = self.get_duration_minutes()
        return duration and duration > self.allowed_duration_minutes