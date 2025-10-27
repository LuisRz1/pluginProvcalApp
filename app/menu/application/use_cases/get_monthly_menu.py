from dataclasses import dataclass
from typing import List, Dict, Any
from app.menu.application.ports.monthly_menu_repository import MonthlyMenuRepository
from app.menu.application.ports.menu_day_repository import MenuDayRepository

@dataclass(frozen=True)
class GetMonthlyMenuQuery:
    year: int
    month: int

class GetMonthlyMenuUseCase:
    def __init__(self, menu_repo: MonthlyMenuRepository, day_repo: MenuDayRepository):
        self.menu_repo = menu_repo
        self.day_repo = day_repo

    async def execute(self, q: GetMonthlyMenuQuery) -> List[Dict[str, Any]]:
        menu = await self.menu_repo.find_by_year_month(q.year, q.month)
        if not menu:
            return []
        days = await self.day_repo.list_by_menu(menu.id)
        return [
            dict(
                id=d.id, date=str(d.date),
                breakfast=d.breakfast, lunch=d.lunch, dinner=d.dinner,
                is_holiday=d.is_holiday, nutrition_flags=d.nutrition_flags
            )
            for d in days
        ]
