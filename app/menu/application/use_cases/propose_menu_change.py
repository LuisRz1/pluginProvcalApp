from dataclasses import dataclass
from datetime import date
from typing import List, Optional
import uuid

from app.menu.application.ports.menu_change_repository import MenuChangeRepository
from app.menu.application.ports.daily_menu_repository import DailyMenuRepository
from app.menu.application.ports.meal_repository import MealRepository
from app.menu.application.ports.meal_component_repository import MealComponentRepository
from app.menu.domain.menu_change_request import MenuChangeRequest
from app.menu.domain.menu_enums import MealType, ChangeStatus
from app.menu.domain.meal_component import MealComponent, GENERIC_COMPONENT_TYPE_ID

@dataclass(frozen=True)
class MenuChangeItem:
    menu_day_id: str   # mantiene el nombre por compatibilidad con FE; es daily_menu_id
    day_date: date
    meal_type: MealType
    new_value: str
    reason: str
    emergency: bool = False

class ProposeMenuChangeUseCase:
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

    async def execute(self, requested_by: str, items: List[MenuChangeItem]) -> List[MenuChangeRequest]:
        results: List[MenuChangeRequest] = []
        batch_id = str(uuid.uuid4())

        for item in items:
            # 1) validar día
            day = await self.daily_repo.find_by_id(item.menu_day_id)
            if not day or str(day.date) != str(item.day_date):
                # id/fecha no corresponden
                raise ValueError("El daily_menu_id no coincide con la fecha indicada")

            # 2) obtener comida y su primer componente como 'old_value'
            meal = await self.meal_repo.find_by_daily_and_type(str(day.id), item.meal_type)
            old_value = ""
            if meal:
                comps = await self.meal_component_repo.list_by_meal(str(meal.id))
                old_value = comps[0].dish_name if comps else ""
            else:
                # si no existe comida aún, la creamos vacía para poder aplicar emergencia
                from app.menu.domain.meal import Meal
                meal = await self.meal_repo.find_by_daily_and_type(str(day.id), item.meal_type)
                if not meal:
                    # creamos usando bulk_replace (modo simple: reemplazamos las 3 con las existentes)
                    existing = await self.meal_repo.list_by_daily_menu(str(day.id))
                    existing_types = {m.meal_type for m in existing}
                    if item.meal_type not in existing_types:
                        existing.append(Meal(id=None, daily_menu_id=str(day.id), meal_type=item.meal_type, total_kcal=None))
                        await self.meal_repo.bulk_replace_for_daily_menu(str(day.id), existing)
                        meal = await self.meal_repo.find_by_daily_and_type(str(day.id), item.meal_type)

            # 3) crear solicitud
            req = MenuChangeRequest(
                id=None,
                daily_menu_id=str(day.id),
                day_date=day.date,
                meal_type=item.meal_type,
                old_value=old_value,
                new_value=item.new_value,
                reason=item.reason,
                status=ChangeStatus.PENDING,
                requested_by=requested_by,
                batch_id=batch_id,
            )

            # 4) si es emergencia, aplicamos inmediatamente al primer componente
            if item.emergency and meal:
                comps = await self.meal_component_repo.list_by_meal(str(meal.id))
                if comps:
                    c0 = comps[0]
                    c0.dish_name = item.new_value
                    await self.meal_component_repo.bulk_replace_for_meal(str(meal.id), [c0] + comps[1:])
                else:
                    await self.meal_component_repo.bulk_replace_for_meal(
                        str(meal.id),
                        [
                            MealComponent(
                                id=None,
                                meal_id=str(meal.id),
                                component_type_id=GENERIC_COMPONENT_TYPE_ID,  # seguro
                                dish_name=item.new_value,
                                calories=None,
                                order_position=1,
                            )
                        ],
                    )
                req.mark_emergency_applied()

            saved = await self.change_repo.save(req)
            results.append(saved)

        return results
