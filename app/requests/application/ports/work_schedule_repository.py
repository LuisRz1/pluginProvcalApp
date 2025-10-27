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
    shift_type: str          # Ej: "morning", "afternoon", "night", etc.
    start_time: time
    end_time: time
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None

class WorkScheduleRepository(ABC):
    """
    Consultas de lectura sobre horarios de trabajo vigentes según work_schedules.
    """

    @abstractmethod
    async def find_shift_by_id(self, shift_id: str) -> Optional[WorkShiftSummary]:
        """Obtiene el turno (tal cual está en work_schedules) por ID"""

    @abstractmethod
    async def find_user_shift_on(self, check_date: date, user_id: str) -> Optional[WorkShiftSummary]:
        """
        Devuelve el turno aplicable para esa fecha:
        aquel donde effective_from <= check_date <= effective_until (o until es NULL)
        y is_active = True.
        """