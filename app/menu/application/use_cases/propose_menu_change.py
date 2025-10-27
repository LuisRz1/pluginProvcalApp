from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional
import uuid

from app.menu.application.ports.menu_change_repository import MenuChangeRepository
from app.menu.application.ports.menu_day_repository import MenuDayRepository
from app.menu.domain.menu_change_request import MenuChangeRequest
from app.menu.domain.menu_enums import MealType, ChangeStatus

@dataclass(frozen=True)
class MenuChangeItem:
    menu_day_id: str
    day_date: date
    meal_type: MealType
    new_value: str
    reason: str
    emergency: bool = False

@dataclass(frozen=True)
class ProposeMenuChangeCommand:
    requester_id: str
    items: List[MenuChangeItem]

class ProposeMenuChangeUseCase:
    def __init__(self, change_repo: MenuChangeRepository, day_repo: MenuDayRepository):
        self.change_repo = change_repo
        self.day_repo = day_repo

    async def execute(self, cmd: ProposeMenuChangeCommand) -> List[MenuChangeRequest]:
        batch_id: Optional[str] = None
        if len(cmd.items) > 1:
            batch_id = str(uuid.uuid4())

        results: List[MenuChangeRequest] = []

        for item in cmd.items:
            # 1. Traemos el día real desde BD usando menu_day_id
            day = await self.day_repo.find_by_id(item.menu_day_id)
            if not day:
                # Esto protege contra IDs inválidos desde el front
                raise ValueError(f"MenuDay {item.menu_day_id} no existe")

            # 2. Determinamos el valor anterior (old_value) según meal_type
            if item.meal_type == MealType.BREAKFAST:
                old_val = day.breakfast
            elif item.meal_type == MealType.LUNCH:
                old_val = day.lunch
            elif item.meal_type == MealType.DINNER:
                old_val = day.dinner
            else:
                # Si llega algo raro, preferimos explotar antes que grabar basura
                raise ValueError(f"Tipo de comida inválido: {item.meal_type}")

            # 3. Creamos la solicitud de cambio
            req = MenuChangeRequest(
               id=None,
               menu_day_id=item.menu_day_id,
               day_date=item.day_date,  # redundante pero útil p/queries por mes
               meal_type=item.meal_type,
               old_value=old_val,
               new_value=item.new_value,
               reason=item.reason,
               requested_by=cmd.requester_id,
               batch_id=batch_id,
            )

            # 4. Si es emergencia:
            #    - marcamos emergency_applied en la request
            #    - actualizamos el menú del día INMEDIATAMENTE
            if item.emergency:
                # Cambiar estado de la solicitud a "emergency_applied"
                req.mark_emergency_applied()

                # Actualizamos el plato en el MenuDay real
                day.set_meal(item.meal_type.value, item.new_value)
                await self.day_repo.save(day)

            # 5. Guardamos la solicitud en BD (ya sea pendiente o emergencia)
            saved_req = await self.change_repo.save(req)
            results.append(saved_req)

        return results
