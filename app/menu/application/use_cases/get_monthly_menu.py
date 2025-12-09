from dataclasses import dataclass
from typing import List, Dict, Any

from app.menu.application.ports.monthly_menu_repository import MonthlyMenuRepository
from app.menu.application.ports.weekly_menu_repository import WeeklyMenuRepository
from app.menu.application.ports.daily_menu_repository import DailyMenuRepository
from app.menu.application.ports.meal_repository import MealRepository
from app.menu.application.ports.meal_component_repository import MealComponentRepository
from app.menu.domain.menu_enums import MealType

@dataclass(frozen=True)
class GetMonthlyMenuQuery:
    year: int
    month: int

class GetMonthlyMenuUseCase:
    """
    Devuelve una lista simple de días con labels (breakfast/lunch/dinner),
    compatible con el FE actual (MenuDayInfo).
    """
    def __init__(
        self,
        menu_repo: MonthlyMenuRepository,
        weekly_repo: WeeklyMenuRepository,
        day_repo: DailyMenuRepository,
        meal_repo: MealRepository,
        meal_component_repo: MealComponentRepository,
    ):
        self.menu_repo = menu_repo
        self.weekly_repo = weekly_repo
        self.day_repo = day_repo
        self.meal_repo = meal_repo
        self.meal_component_repo = meal_component_repo

    async def _meal_text(self, daily_id: str, mt: MealType) -> str:
        m = await self.meal_repo.find_by_daily_and_type(daily_id, mt)
        if not m:
            return ""
        comps = await self.meal_component_repo.list_by_meal(str(m.id))
        return comps[0].dish_name if comps else ""

    async def execute(self, q: GetMonthlyMenuQuery) -> List[Dict[str, Any]]:
        menu = await self.menu_repo.find_by_year_month(q.year, q.month)
        if not menu:
            return []

        weeks = await self.weekly_repo.list_by_month(str(menu.id))
        days = []
        for w in weeks:
            days.extend(await self.day_repo.list_by_week(str(w.id)))
        # ordenar por fecha
        days.sort(key=lambda d: d.date)

        out: List[Dict[str, Any]] = []
        for d in days:
            b = await self._meal_text(str(d.id), MealType.BREAKFAST)
            l = await self._meal_text(str(d.id), MealType.LUNCH)
            dn = await self._meal_text(str(d.id), MealType.DINNER)
            out.append(dict(
                id=str(d.id),
                date=str(d.date),
                breakfast=b,
                lunch=l,
                dinner=dn,
                is_holiday=d.is_holiday,
                nutrition_flags={},  # sin uso en el modelo normalizado; se deja vacío para compatibilidad
            ))
        return out
