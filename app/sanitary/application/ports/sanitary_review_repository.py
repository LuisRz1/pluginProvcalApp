from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from uuid import UUID

from app.sanitary.domain.sanitary_review import SanitaryReview


class SanitaryReviewRepository(ABC):
    """
    Puerto de acceso a persistencia para las revisiones de sanidad (RevisionSanidad).

    Operaciones alineadas con tu E-R y las pantallas:
      - Registrar una revisión.
      - Obtener una revisión por id (para detalles si hiciera falta).
      - Listar revisiones de una política en un rango de fechas
        (para el historial con filtros de 6m, 1 año, 2 años).
      - Obtener la última revisión de una política (para calcular la 'próxima').
    """

    @abstractmethod
    async def get_by_id(self, review_id: UUID) -> Optional[SanitaryReview]:
        """
        Devuelve una revisión por su ID, o None si no existe.
        """
        raise NotImplementedError

    @abstractmethod
    async def save(self, review: SanitaryReview) -> SanitaryReview:
        """
        Crea una nueva revisión en la base de datos.
        (En este módulo asumimos que las revisiones no se editan de momento:
         lo normal es registrar un nuevo control cada vez.)
        """
        raise NotImplementedError

    @abstractmethod
    async def list_by_policy_and_period(
        self,
        policy_id: UUID,
        start_date: date,
        end_date: date,
    ) -> List[SanitaryReview]:
        """
        Lista las revisiones de una política en un rango de fechas [start_date, end_date],
        ordenadas típicamente por fecha descendente para el historial.
        Esto se usará para:
          - Historial con filtros de 6 meses, 1 año, 2 años.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_last_by_policy(self, policy_id: UUID) -> Optional[SanitaryReview]:
        """
        Devuelve la última revisión registrada para una política
        (MAX(fecha)), o None si aún no tiene revisiones.

        Esto permitirá calcular en el caso de uso:
          próxima_revision = ultima_fecha + 30 días
        sin necesidad de guardar ese dato en la BD.
        """
        raise NotImplementedError
