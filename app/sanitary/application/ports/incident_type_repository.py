from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.sanitary.domain.incident_type import IncidentType


class IncidentTypeRepository(ABC):
    """
    Puerto de acceso a persistencia para los tipos de incidencia (TipoIncidencia).

    Operaciones alineadas con tu E-R e interfaces:
      - Obtener por id.
      - Listar por política.
      - Guardar (crear / actualizar).
    """

    @abstractmethod
    async def get_by_id(self, incident_type_id: UUID) -> Optional[IncidentType]:
        """
        Devuelve un tipo de incidencia por su ID, o None si no existe.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_by_policy(self, policy_id: UUID, only_active: bool = True) -> List[IncidentType]:
        """
        Lista los tipos de incidencia asociados a una política.
        Por defecto, solo devuelve los que están activos (esta_activa = true),
        que son los que se muestran en el combo de la UI al marcar 'Inconforme'.
        """
        raise NotImplementedError

    @abstractmethod
    async def save(self, incident_type: IncidentType) -> IncidentType:
        """
        Crea o actualiza un tipo de incidencia en la base de datos.
        """
        raise NotImplementedError
