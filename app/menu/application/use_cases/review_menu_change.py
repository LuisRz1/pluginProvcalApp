from dataclasses import dataclass
from typing import Optional
from app.menu.application.ports.menu_change_repository import MenuChangeRepository
from app.menu.application.ports.menu_day_repository import MenuDayRepository
from app.menu.domain.menu_enums import ChangeStatus, MealType

@dataclass(frozen=True)
class ReviewMenuChangeCommand:
    change_id: str
    decider_id: str
    approve: bool
    notes: Optional[str] = None

class ReviewMenuChangeUseCase:
    def __init__(self, change_repo: MenuChangeRepository, day_repo: MenuDayRepository):
        self.change_repo = change_repo
        self.day_repo = day_repo

    async def execute(self, cmd: ReviewMenuChangeCommand):
        req = await self.change_repo.find_by_id(cmd.change_id)
        if not req:
            raise ValueError("Cambio no encontrado")

        if cmd.approve:
            req.approve(cmd.decider_id)
            # aplicar en MenuDay
            day = await self.day_repo.find_by_id(req.menu_day_id)  # ajusta firma real
            # si el repo no usa (menu_id, date), provee otro método por id
            if day:
                day.set_meal(req.meal_type.value, req.new_value)
                await self.day_repo.save(day)
        else:
            req.reject(cmd.decider_id, cmd.notes)

        await self.change_repo.save(req)
        return req
