from abc import ABC, abstractmethod
from typing import List, Optional

from app.menu.domain.component_type import ComponentType


class ComponentTypeRepository(ABC):
    """
    Puerto de acceso a la tabla component_types.
    Permite buscar por nombre, crear y listar los tipos de componente
    (BEBIDA CALIENTE, PLATO CALIENTE, ENTRADA, SOPA, GUARNICIÓN 1, etc.).
    """

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[ComponentType]:
        """
        Devuelve el tipo de componente con ese nombre (component_name),
        o None si no existe.
        """
        ...

    @abstractmethod
    async def create(self, component_type: ComponentType) -> ComponentType:
        """
        Crea un nuevo tipo de componente.
        """
        ...

    @abstractmethod
    async def list_all(self) -> List[ComponentType]:
        """
        Lista todos los tipos de componente ordenados por display_order.
        """
        ...
