from dataclasses import dataclass
from typing import Optional


@dataclass
class ComponentType:
    """
    Tipo de componente de una comida
    (por ejemplo: BEBIDA CALIENTE, PLATO CALIENTE, ENTRADA, SOPA, GUARNICIÓN 1, etc.).
    Mapea a la tabla component_types.
    """
    id: Optional[str]
    name: str
    display_order: int = 0
