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
    def __init__(self, menu_repo: MonthlyMenuRepository, day_repo: MenuDayRepository):
        self.menu_repo = menu_repo
        self.day_repo = day_repo

    async def execute(self, q: ExportMonthlyMenuQuery) -> ExportMonthlyMenuResult:
        # Generación real del PDF/XLSX queda a tu elección de lib
        menu = await self.menu_repo.find_by_year_month(q.year, q.month)
        if not menu:
            return ExportMonthlyMenuResult("error", "No existe menú", None)
        days = await self.day_repo.list_by_menu(menu.id)
        # TODO: generar archivo. Retornar ruta o bytes en storage.
        return ExportMonthlyMenuResult("ok", "Export listo (implementación pendiente)", None)
