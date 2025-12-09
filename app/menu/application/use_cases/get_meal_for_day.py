from dataclasses import dataclass
from datetime import date
from typing import Optional, Dict, Any, List

from app.menu.application.ports.daily_menu_repository import DailyMenuRepository
from app.menu.application.ports.meal_repository import MealRepository
from app.menu.application.ports.meal_component_repository import MealComponentRepository
from app.menu.domain.menu_enums import MealType

@dataclass(frozen=True)
class GetMealForDayQuery:
    day: date
    meal_type: MealType

def _component_to_dict(c) -> Dict[str, Any]:
    return dict(
        id=str(c.id),
        meal_id=str(c.meal_id),
        component_type_id=str(c.component_type_id),
        dish_name=c.dish_name,
        calories=c.calories,
        order_position=c.order_position,
    )

class GetMealForDayUseCase:
    def __init__(
        self,
        day_repo: DailyMenuRepository,
        meal_repo: MealRepository,
        component_repo: MealComponentRepository,
    ):
        self.day_repo = day_repo
        self.meal_repo = meal_repo
        self.component_repo = component_repo

    async def execute(self, q: GetMealForDayQuery) -> Optional[Dict[str, Any]]:
        daily = await self.day_repo.find_by_date(q.day)
        if not daily:
            return None
        meal = await self.meal_repo.find_by_daily_and_type(str(daily.id), q.meal_type)
        if not meal:
            return dict(
                daily_menu_id=str(daily.id),
                date=str(daily.date),
                day_of_week=daily.day_of_week,
                is_holiday=daily.is_holiday,
                meal=None,
            )
        components = await self.component_repo.list_by_meal(str(meal.id))
        return dict(
            daily_menu_id=str(daily.id),
            date=str(daily.date),
            day_of_week=daily.day_of_week,
            is_holiday=daily.is_holiday,
            meal=dict(
                id=str(meal.id),
                daily_menu_id=str(meal.daily_menu_id),
                meal_type=meal.meal_type.value,
                total_kcal=meal.total_kcal,
                components=[_component_to_dict(c) for c in components],
            ),
        )
