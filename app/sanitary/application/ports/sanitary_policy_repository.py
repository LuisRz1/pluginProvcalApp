from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.sanitary.domain.sanitary_policy import SanitaryPolicy


class SanitaryPolicyRepository(ABC):
    """
    Puerto de acceso a persistencia para las políticas de sanidad (PoliticaSanidad).

    No definimos nada que no exista en tu E-R ni en las interfaces:
      - Obtener una política por id.
      - Listar todas / solo activas.
      - Guardar (crear / actualizar) una política.
    """

    @abstractmethod
    async def get_by_id(self, policy_id: UUID) -> Optional[SanitaryPolicy]:
        """
        Devuelve una política por su ID, o None si no existe.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> List[SanitaryPolicy]:
        """
        Lista todas las políticas (activas e inactivas).
        Útil para administración interna.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_active(self) -> List[SanitaryPolicy]:
        """
        Lista únicamente las políticas activas (esta_activa = true),
        que son las que se muestran al nutricionista en la UI.
        """
        raise NotImplementedError

    @abstractmethod
    async def save(self, policy: SanitaryPolicy) -> SanitaryPolicy:
        """
        Crea o actualiza una política en la base de datos.
        """
        raise NotImplementedError
