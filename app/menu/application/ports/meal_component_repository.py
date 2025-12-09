from abc import ABC, abstractmethod
from typing import List, Optional

from app.menu.domain.meal_component import MealComponent


class MealComponentRepository(ABC):
    @abstractmethod
    async def bulk_replace_for_meal(
        self,
        meal_id: str,
        components: List[MealComponent],
    ) -> None:
        """
        Reemplaza todos los componentes de una comida.
        """
        ...

    @abstractmethod
    async def list_by_meal(self, meal_id: str) -> List[MealComponent]:
        ...

    @abstractmethod
    async def find_by_id(self, meal_component_id: str) -> Optional[MealComponent]:
        ...
