from abc import ABC, abstractmethod
from typing import List, Optional

from app.menu.domain.meal import Meal
from app.menu.domain.menu_enums import MealType


class MealRepository(ABC):
    @abstractmethod
    async def bulk_replace_for_daily_menu(
        self,
        daily_menu_id: str,
        meals: List[Meal],
    ) -> None:
        """
        Reemplaza todas las comidas de un DailyMenu.
        """
        ...

    @abstractmethod
    async def list_by_daily_menu(self, daily_menu_id: str) -> List[Meal]:
        ...

    @abstractmethod
    async def find_by_daily_and_type(
        self,
        daily_menu_id: str,
        meal_type: MealType,
    ) -> Optional[Meal]:
        ...

    @abstractmethod
    async def find_by_id(self, meal_id: str) -> Optional[Meal]:
        ...
