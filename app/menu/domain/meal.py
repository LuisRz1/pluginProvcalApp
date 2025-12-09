from dataclasses import dataclass
from typing import Optional

from app.menu.domain.menu_enums import MealType


@dataclass
class Meal:
    """
    Representa una comida (desayuno / almuerzo / cena) para un día.
    Mapea a la tabla meals.
    """
    id: Optional[str]
    daily_menu_id: str
    meal_type: MealType
    total_kcal: Optional[float] = None
