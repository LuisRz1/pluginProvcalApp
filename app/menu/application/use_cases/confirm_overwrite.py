from dataclasses import dataclass
from typing import List, Dict, Any
import io
from datetime import date

from app.menu.domain.monthly_menu import MonthlyMenu
from app.menu.domain.menu_day import MenuDay
from app.menu.domain.menu_enums import MenuStatus
from app.menu.application.ports.monthly_menu_repository import MonthlyMenuRepository
from app.menu.application.ports.menu_day_repository import MenuDayRepository

try:
    import pandas as pd
except ImportError:
    pd = None

@dataclass(frozen=True)
class ConfirmOverwriteCommand:
    user_id: str
    filename: str
    file_bytes: bytes
    year: int
    month: int

@dataclass
class ConfirmOverwriteResult:
    status: str
    message: str
    days: List[Dict[str, Any]]

class ConfirmOverwriteUseCase:
    def __init__(self, menu_repo: MonthlyMenuRepository, day_repo: MenuDayRepository):
        self.menu_repo = menu_repo
        self.day_repo = day_repo

    async def execute(self, cmd: ConfirmOverwriteCommand) -> ConfirmOverwriteResult:
        if pd is None:
            return ConfirmOverwriteResult("error", "Pandas no disponible", [])

        existing = await self.menu_repo.find_by_year_month(cmd.year, cmd.month)
        if not existing:
            return ConfirmOverwriteResult("error", "No hay menú previo para sobrescribir", [])

        df = pd.read_excel(io.BytesIO(cmd.file_bytes))
        df.columns = [c.strip().lower() for c in df.columns]
        df["date"] = pd.to_datetime(df["date"]).dt.date

        days = [
            MenuDay(
                id=None,
                menu_id=existing.id,
                date=r["date"],
                breakfast=str(r["breakfast"] or ""),
                lunch=str(r["lunch"] or ""),
                dinner=str(r["dinner"] or ""),
            )
            for _, r in df.iterrows()
        ]
        await self.day_repo.bulk_replace(existing.id, days)

        preview = [
            dict(date=str(d.date), breakfast=d.breakfast, lunch=d.lunch, dinner=d.dinner)
            for d in days
        ]
        return ConfirmOverwriteResult("ok", "Menú reemplazado", preview)
