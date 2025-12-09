from abc import ABC, abstractmethod
from typing import List, Optional

from app.menu.domain.weekly_menu import WeeklyMenu


class WeeklyMenuRepository(ABC):
    @abstractmethod
    async def bulk_replace(self, monthly_menu_id: str, weeks: List[WeeklyMenu]) -> None:
        """
        Reemplaza todas las semanas de un menú mensual por las indicadas.
        """
        ...

    @abstractmethod
    async def list_by_month(self, monthly_menu_id: str) -> List[WeeklyMenu]:
        ...

    @abstractmethod
    async def find_by_id(self, weekly_menu_id: str) -> Optional[WeeklyMenu]:
        ...
