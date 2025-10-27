from dataclasses import dataclass
from typing import List, Dict, Any
from app.menu.application.ports.menu_change_repository import MenuChangeRepository

@dataclass(frozen=True)
class GetMenuChangeHistoryQuery:
    year: int
    month: int

class GetMenuChangeHistoryUseCase:
    def __init__(self, change_repo: MenuChangeRepository):
        self.change_repo = change_repo

    async def execute(self, q: GetMenuChangeHistoryQuery) -> List[Dict[str, Any]]:
        changes = await self.change_repo.list_for_month(q.year, q.month)
        return [
            dict(
                id=c.id,
                date=str(c.day_date),
                meal_type=c.meal_type.value,
                old_value=c.old_value,
                new_value=c.new_value,
                status=c.status.value,
                requested_by=c.requested_by,
                decided_by=c.decided_by,
                decided_at=str(c.decided_at) if c.decided_at else None,
                notes=c.notes_from_decider
            )
            for c in changes
        ]
