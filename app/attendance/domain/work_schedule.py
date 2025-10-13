"""Entidad de horario laboral"""
from dataclasses import dataclass, field
from datetime import time, date, datetime, timezone
from typing import Optional, List
from enum import Enum
from app.building_blocks.exceptions import DomainException

class ShiftType(Enum):
    """Tipos de turno"""
    MORNING = "morning"         # Mañana: 6 AM - 2 PM
    AFTERNOON = "afternoon"     # Tarde: 2 PM - 10 PM
    NIGHT = "night"            # Noche: 10 PM - 6 AM
    FULL_DAY = "full_day"      # Jornada completa: 8 AM - 5 PM
    CUSTOM = "custom"          # Personalizado

@dataclass
class WorkSchedule:
    """
    Horario de trabajo de un empleado.
    Permite horarios fijos y rotativos.
    """
    id: Optional[str] = None
    user_id: str = ""
    shift_type: ShiftType = ShiftType.FULL_DAY

    # Horarios
    start_time: time = time(9, 0)
    end_time: time = time(18, 0)

    # Días laborables (0=Lunes, 6=Domingo)
    working_days: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4,5])

    # Tolerancia para tardanza (minutos)
    late_tolerance_minutes: int = 15

    # Break time permitido (minutos)
    break_duration_minutes: int = 30

    # Vigencia
    is_active: bool = True
    effective_from: date = field(default_factory=date.today)
    effective_until: Optional[date] = None

    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None  # ID del admin que lo creó
    notes: Optional[str] = None

    def __post_init__(self):
        self._validate()

    def _validate(self):
        """Validaciones del horario"""
        if self.start_time >= self.end_time:
            # Permitir turnos nocturnos que cruzan medianoche
            if self.shift_type != ShiftType.NIGHT:
                raise DomainException(
                    "La hora de inicio debe ser menor a la hora de fin"
                )

        if not self.working_days:
            raise DomainException("Debe tener al menos un día laboral")

        if any(day < 0 or day > 6 for day in self.working_days):
            raise DomainException("Días laborables deben estar entre 0 (Lunes) y 6 (Domingo)")

        if self.late_tolerance_minutes < 0:
            raise DomainException("Tolerancia no puede ser negativa")

    def is_working_day(self, check_date: date) -> bool:
        """Verifica si una fecha es día laboral según este horario"""
        weekday = check_date.weekday()  # 0=Lunes, 6=Domingo
        return weekday in self.working_days

    def is_valid_for_date(self, check_date: date) -> bool:
        """Verifica si este horario es válido para una fecha específica"""
        if not self.is_active:
            return False

        if check_date < self.effective_from:
            return False

        if self.effective_until and check_date > self.effective_until:
            return False

        return True

    def deactivate(self, end_date: Optional[date] = None):
        """Desactiva el horario"""
        self.is_active = False
        if end_date:
            self.effective_until = end_date
        else:
            self.effective_until = date.today()

    def get_total_hours_per_day(self) -> float:
        """Calcula las horas de trabajo por día"""
        # Convertir a datetime para calcular diferencia
        start = datetime.combine(date.today(), self.start_time)
        end = datetime.combine(date.today(), self.end_time)

        # Si es turno nocturno (cruza medianoche)
        if self.shift_type == ShiftType.NIGHT and end < start:
            end = end.replace(day=end.day + 1)

        delta = end - start
        hours = delta.total_seconds() / 3600

        # Restar tiempo de descanso
        break_hours = self.break_duration_minutes / 60
        return hours - break_hours