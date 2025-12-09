import base64, csv, io
from typing import Dict, Any, List
from datetime import date

from app.menu.application.ports.monthly_menu_repository import MonthlyMenuRepository
from app.menu.application.ports.weekly_menu_repository import WeeklyMenuRepository
from app.menu.application.ports.daily_menu_repository import DailyMenuRepository
from app.menu.application.ports.meal_repository import MealRepository
from app.menu.application.ports.meal_component_repository import MealComponentRepository
from app.menu.domain.menu_enums import MealType

class ExportMonthlyMenuUseCase:
    def __init__(
        self,
        monthly_repo: MonthlyMenuRepository,
        weekly_repo: WeeklyMenuRepository,
        daily_repo: DailyMenuRepository,
        meal_repo: MealRepository,
        meal_component_repo: MealComponentRepository,
    ) -> None:
        self.monthly_repo = monthly_repo
        self.weekly_repo = weekly_repo
        self.daily_repo = daily_repo
        self.meal_repo = meal_repo
        self.meal_component_repo = meal_component_repo

    async def execute(self, year: int, month: int) -> Dict[str, Any]:
        monthly = await self.monthly_repo.find_by_year_month(year, month)
        if not monthly:
            return {"status": "error", "message": "No existe menú para ese mes"}
        weeks = await self.weekly_repo.list_by_month(str(monthly.id))
        # recolectar días
        days = []
        for w in weeks:
            days.extend(await self.daily_repo.list_by_week(str(w.id)))

        # ordenar por fecha
        days.sort(key=lambda d: d.date)

        async def meal_text(daily_id: str, mt: MealType) -> str:
            m = await self.meal_repo.find_by_daily_and_type(daily_id, mt)
            if not m:
                return ""
            comps = await self.meal_component_repo.list_by_meal(str(m.id))
            return comps[0].dish_name if comps else ""

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["date", "breakfast", "lunch", "dinner"])
        for d in days:
            b = await meal_text(str(d.id), MealType.BREAKFAST)
            l = await meal_text(str(d.id), MealType.LUNCH)
            dn = await meal_text(str(d.id), MealType.DINNER)
            writer.writerow([str(d.date), b, l, dn])

        content = output.getvalue().encode("utf-8")
        return {
            "status": "ok",
            "filename": f"menu_{year}_{month:02d}.csv",
            "content_base64": base64.b64encode(content).decode("ascii"),
        }
