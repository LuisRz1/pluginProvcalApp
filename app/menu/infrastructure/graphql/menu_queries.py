import strawberry
from typing import List, Optional
from datetime import date
from app.menu.application.use_cases.get_monthly_menu import GetMonthlyMenuUseCase, GetMonthlyMenuQuery
from app.menu.application.use_cases.get_menu_change_history import GetMenuChangeHistoryUseCase, GetMenuChangeHistoryQuery
from .menu_types import MonthlyMenuCalendar, MenuDayInfo, MenuChangeInfo, ExportedFile
from ...application.use_cases.export_monthly_menu import ExportMonthlyMenuUseCase

def _require_auth(info):
    if not info.context.get("current_user"):
        raise Exception("No autenticado")

@strawberry.type
class MenuQueries:
    @strawberry.field
    async def menu(self, info, year: int, month: int) -> Optional[MonthlyMenuCalendar]:
        days = await GetMonthlyMenuUseCase(
            info.context["monthly_menu_repository"],
            info.context["menu_day_repository"]
        ).execute(GetMonthlyMenuQuery(year, month))

        if not days:
            return None

        return MonthlyMenuCalendar(
            year=year, month=month,
            days=[MenuDayInfo(
                id=d["id"],
                date=date.fromisoformat(d["date"]),
                breakfast=d["breakfast"],
                lunch=d["lunch"],
                dinner=d["dinner"],
                is_holiday=d["is_holiday"],
                nutrition_flags=d["nutrition_flags"],
            ) for d in days]
        )

    @strawberry.field
    async def menu_change_history(self, info, year: int, month: int) -> List[MenuChangeInfo]:
        data = await GetMenuChangeHistoryUseCase(info.context["menu_change_repository"])\
            .execute(GetMenuChangeHistoryQuery(year, month))
        from datetime import datetime as _dt
        def _parse(dt):
            return _dt.fromisoformat(dt) if dt else None
        return [
            MenuChangeInfo(
                id=x["id"],
                date=date.fromisoformat(x["date"]),
                meal_type=x["meal_type"],
                old_value=x["old_value"],
                new_value=x["new_value"],
                status=x["status"],
                requested_by=x["requested_by"],
                decided_by=x["decided_by"],
                decided_at=_parse(x["decided_at"]),
                notes=x["notes"],
                batch_id=x["batch_id"],
            ) for x in data
        ]

    @strawberry.field
    async def export_monthly_menu(self, info, year: int, month: int) -> ExportedFile:
        uc = ExportMonthlyMenuUseCase(
            info.context["monthly_menu_repository"],
            info.context["menu_day_repository"],
        )
        res = await uc.execute(year, month)
        return ExportedFile(**res)