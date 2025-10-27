from abc import ABC, abstractmethod
from typing import List, Optional
from app.menu.domain.menu_change_request import MenuChangeRequest
from datetime import date

class MenuChangeRepository(ABC):
    @abstractmethod
    async def save(self, req: MenuChangeRequest) -> MenuChangeRequest: ...
    @abstractmethod
    async def find_by_id(self, change_id: str) -> Optional[MenuChangeRequest]: ...
    @abstractmethod
    async def list_for_month(self, year: int, month: int) -> List[MenuChangeRequest]: ...
    @abstractmethod
    async def list_by_batch(self, batch_id: str) -> List[MenuChangeRequest]: ...
