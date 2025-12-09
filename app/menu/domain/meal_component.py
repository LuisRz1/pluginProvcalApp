from dataclasses import dataclass
from typing import Optional


# Tipo genérico mientras no haya catálogo formal de tipos de componente.
# Lo usamos para satisfacer la columna UUID de component_type_id.
GENERIC_COMPONENT_TYPE_ID = "00000000-0000-0000-0000-000000000000"


@dataclass
class MealComponent:
    """
    Representa un componente dentro de una comida
    (entrada, fondo, guarnición, refresco, etc.).
    Mapea a la tabla meal_components.
    """
    id: Optional[str]
    meal_id: str
    component_type_id: str
    dish_name: str
    calories: Optional[float] = None
    order_position: int = 0
