from dataclasses import dataclass
from typing import Optional


@dataclass
class WeeklyMenu:
    """
    Representa una semana dentro de un menú mensual.
    Mapea a la tabla weekly_menus.
    """
    id: Optional[str]
    monthly_menu_id: str
    week_number: int
    title: Optional[str] = None
