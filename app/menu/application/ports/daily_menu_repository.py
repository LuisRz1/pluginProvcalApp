from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from app.menu.domain.daily_menu import DailyMenu


class DailyMenuRepository(ABC):
    @abstractmethod
    async def bulk_replace_for_week(
        self,
        weekly_menu_id: str,
        days: List[DailyMenu],
    ) -> None:
        """
        Reemplaza todos los días de una semana por los indicados.
        """
        ...

    @abstractmethod
    async def list_by_week(self, weekly_menu_id: str) -> List[DailyMenu]:
        ...

    @abstractmethod
    async def find_by_date(self, day: date) -> Optional[DailyMenu]:
        """
        Busca el DailyMenu por fecha (asumiendo un menú único activo para esa fecha).
        """
        ...

    @abstractmethod
    async def find_by_id(self, daily_menu_id: str) -> Optional[DailyMenu]:
        ...
