from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.sanitary.domain.sanitary_company import SanitaryCompany


class SanitaryCompanyRepository(ABC):
    """
    Puerto de acceso a persistencia para las empresas especializadas
    de sanidad (Empresa del E-R de sanidad).

    Necesitamos:
      - Obtener por id (para mostrar los datos cuando se guarda una revisión).
      - Listar (para poblar el combo 'Empresa a contactar' en la UI).
      - Guardar (crear / actualizar) empresas.
    """

    @abstractmethod
    async def get_by_id(self, company_id: UUID) -> Optional[SanitaryCompany]:
        """
        Devuelve una empresa por su ID, o None si no existe.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> List[SanitaryCompany]:
        """
        Lista todas las empresas disponibles para ser contactadas
        en caso de revisión INCONFORME.
        """
        raise NotImplementedError

    @abstractmethod
    async def save(self, company: SanitaryCompany) -> SanitaryCompany:
        """
        Crea o actualiza una empresa de sanidad en la base de datos.
        """
        raise NotImplementedError
