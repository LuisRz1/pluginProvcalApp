from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class DailyMenu:
    """
    Representa el menú de un día específico dentro de una semana.
    Mapea a la tabla daily_menus.
    """
    id: Optional[str]
    weekly_menu_id: str
    date: date
    day_of_week: Optional[str] = None
    is_holiday: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
