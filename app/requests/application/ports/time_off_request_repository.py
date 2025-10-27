"""Puerto para repositorio de solicitudes de tiempo libre (vacaciones/permisos)"""
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date
from app.requests.domain.time_off_request import TimeOffRequest

class TimeOffRequestRepository(ABC):
    """Contrato para persistencia y consultas de TimeOffRequest"""

    @abstractmethod
    async def save(self, request: TimeOffRequest) -> TimeOffRequest:
        """Guarda o actualiza una solicitud"""

    @abstractmethod
    async def find_by_id(self, request_id: str) -> Optional[TimeOffRequest]:
        """Busca una solicitud por ID"""

    @abstractmethod
    async def find_by_user(self, user_id: str, limit: int = 50) -> List[TimeOffRequest]:
        """Obtiene las últimas solicitudes de un usuario"""

    @abstractmethod
    async def find_overlaps(self, user_id: str, start: date, end: date) -> List[TimeOffRequest]:
        """
        Devuelve solicitudes que se solapan con el rango [start, end] para el usuario.
        Solo aplica a estados que cuenten (p.ej. pending/approved).
        """
