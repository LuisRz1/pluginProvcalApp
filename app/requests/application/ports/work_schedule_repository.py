"""Puerto de solo lectura para horarios de trabajo (tabla horarios_trabajo)"""
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass
from datetime import date, time

# DTO liviano para no acoplar a la capa de persistencia
@dataclass(frozen=True)
class WorkShiftSummary:
    """Resumen de turno asignado a un usuario en una fecha/registro."""
    id: str
    user_id: str
    shift_type: str          # Ej: "mañana", "tarde", "noche", "jornada_completa", "personalizado"
    start_time: time
    end_time: time
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None

class WorkScheduleRepository(ABC):
    """Consultas de lectura sobre horarios de trabajo"""

    @abstractmethod
    async def find_shift_by_id(self, shift_id: str) -> Optional[WorkShiftSummary]:
        """Obtiene un turno por su ID"""

    @abstractmethod
    async def find_user_shift_on(self, check_date: date, user_id: str) -> Optional[WorkShiftSummary]:
        """
        Obtiene el turno del usuario aplicable para una fecha (considerando vigencia y estado).
        Debe leer desde 'horarios_trabajo' y devolver None si no tiene turno ese día.
        """
