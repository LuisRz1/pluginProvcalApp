"""Puerto para repositorio de solicitudes de intercambio de turnos"""
from abc import ABC, abstractmethod
from typing import Optional, List
from app.requests.domain.shift_swap_request import ShiftSwapRequest

class ShiftSwapRepository(ABC):
    """Contrato para persistencia/consultas de ShiftSwapRequest"""

    @abstractmethod
    async def save(self, swap: ShiftSwapRequest) -> ShiftSwapRequest:
        """Guarda o actualiza una solicitud de intercambio"""

    @abstractmethod
    async def find_by_id(self, swap_id: str) -> Optional[ShiftSwapRequest]:
        """Busca una solicitud de intercambio por ID"""

    @abstractmethod
    async def find_my_swaps(self, user_id: str, limit: int = 50) -> List[ShiftSwapRequest]:
        """
        Lista de intercambios donde el usuario es solicitante (requester) o destinatario (target),
        ordenados del más reciente al más antiguo.
        """
