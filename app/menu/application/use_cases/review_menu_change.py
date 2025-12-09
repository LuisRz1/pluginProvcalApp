from dataclasses import dataclass
from typing import Optional

from app.menu.application.ports.menu_change_repository import MenuChangeRepository
from app.menu.application.ports.daily_menu_repository import DailyMenuRepository
from app.menu.application.ports.meal_repository import MealRepository
from app.menu.application.ports.meal_component_repository import MealComponentRepository
from app.menu.domain.menu_enums import ChangeStatus
from app.menu.domain.meal_component import MealComponent, GENERIC_COMPONENT_TYPE_ID

@dataclass(frozen=True)
class ReviewMenuChangeCommand:
    change_id: str
    approve: bool
    notes: Optional[str] = None
    decider_id: Optional[str] = None

class ReviewMenuChangeUseCase:
    def __init__(
        self,
        change_repo: MenuChangeRepository,
        daily_repo: DailyMenuRepository,
        meal_repo: MealRepository,
        meal_component_repo: MealComponentRepository,
    ) -> None:
        self.change_repo = change_repo
        self.daily_repo = daily_repo
        self.meal_repo = meal_repo
        self.meal_component_repo = meal_component_repo

    async def execute(self, cmd: ReviewMenuChangeCommand):
        req = await self.change_repo.find_by_id(cmd.change_id)
        if not req:
            raise ValueError("Solicitud no encontrada")

        if cmd.approve:
            # aplicar cambio sobre el primer componente de la comida
            meal = await self.meal_repo.find_by_daily_and_type(req.daily_menu_id, req.meal_type)
            if meal:
                comps = await self.meal_component_repo.list_by_meal(str(meal.id))
                if comps:
                    c0 = comps[0]
                    c0.dish_name = req.new_value
                    await self.meal_component_repo.bulk_replace_for_meal(str(meal.id), [c0] + comps[1:])
                else:
                    await self.meal_component_repo.bulk_replace_for_meal(
                        str(meal.id),
                        [
                            MealComponent(
                                id=None,
                                meal_id=str(meal.id),
                                component_type_id=GENERIC_COMPONENT_TYPE_ID,
                                dish_name=req.new_value,
                                calories=None,
                                order_position=0,
                            )
                        ],
                    )
            req.approve(decider_id=(cmd.decider_id or ""))
        else:
            req.reject(decider_id=(cmd.decider_id or ""), notes=cmd.notes)

        return await self.change_repo.save(req)
