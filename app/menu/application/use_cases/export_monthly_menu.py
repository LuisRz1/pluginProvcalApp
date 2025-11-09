import base64
import csv
import io
from dataclasses import dataclass
from typing import Optional
from app.menu.application.ports.monthly_menu_repository import MonthlyMenuRepository
from app.menu.application.ports.menu_day_repository import MenuDayRepository

@dataclass(frozen=True)
class ExportMonthlyMenuQuery:
    year: int
    month: int
    format: str = "pdf"  # o "xlsx"

@dataclass
class ExportMonthlyMenuResult:
    status: str
    message: str
    file_path: Optional[str] = None

class ExportMonthlyMenuUseCase:
    def __init__(self, monthly_repo: MonthlyMenuRepository, menu_day_repo: MenuDayRepository):
        self.monthly_repo = monthly_repo
        self.menu_day_repo = menu_day_repo

    async def execute(self, year: int, month: int):
        monthly = await self.monthly_repo.find_by_year_month(year, month)
        if not monthly:
            return {
                "status": "error",
                "message": "No existe menú para ese mes"
            }

        days = await self.menu_day_repo.list_by_menu(str(monthly.id))

        # armamos un CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["date", "breakfast", "lunch", "dinner", "is_holiday"])
        for d in sorted(days, key=lambda x: x.date):
            writer.writerow([
                d.date.isoformat(),
                d.breakfast,
                d.lunch,
                d.dinner,
                "yes" if d.is_holiday else "no"
            ])

        csv_bytes = output.getvalue().encode("utf-8")
        b64 = base64.b64encode(csv_bytes).decode("utf-8")

        filename = f"menu_{year}_{month:02d}.csv"

        return {
            "status": "ok",
            "filename": filename,
            "content_base64": b64
        }