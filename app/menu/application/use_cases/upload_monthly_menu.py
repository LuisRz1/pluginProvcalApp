import io
import uuid
from dataclasses import dataclass
from datetime import date
from typing import List, Dict, Any, Tuple

from app.menu.domain.monthly_menu import MonthlyMenu
from app.menu.domain.menu_day import MenuDay
from app.menu.domain.menu_enums import MenuStatus
from app.menu.application.ports.monthly_menu_repository import MonthlyMenuRepository
from app.menu.application.ports.menu_day_repository import MenuDayRepository

try:
    import pandas as pd
except ImportError:
    pd = None  # se valida abajo

REQUIRED_COLUMNS = ["date", "breakfast", "lunch", "dinner"]

@dataclass(frozen=True)
class UploadMonthlyMenuCommand:
    user_id: str
    filename: str
    file_bytes: bytes  # contenido XLSX
    year: int
    month: int
    mark_holidays: bool = True  # escenario 12

@dataclass
class UploadMonthlyMenuResult:
    status: str  # "ok" | "conflict" | "error"
    message: str
    preview_days: List[Dict[str, Any]]  # para mostrar en calendario
    template_example: List[str] | None = None

class UploadMonthlyMenuUseCase:
    def __init__(self, menu_repo: MonthlyMenuRepository, day_repo: MenuDayRepository):
        self.menu_repo = menu_repo
        self.day_repo = day_repo

    async def execute(self, cmd: UploadMonthlyMenuCommand) -> UploadMonthlyMenuResult:
        if pd is None:
            return UploadMonthlyMenuResult("error", "Pandas no disponible en el backend", [], None)

        # 1) leer xlsx
        df = pd.read_excel(io.BytesIO(cmd.file_bytes))
        cols = [c.strip().lower() for c in df.columns]
        df.columns = cols

        missing = [c for c in REQUIRED_COLUMNS if c not in cols]
        if missing:
            return UploadMonthlyMenuResult(
                status="error",
                message=f"Faltan columnas: {', '.join(missing)}",
                preview_days=[],
                template_example=REQUIRED_COLUMNS
            )

        # 2) validar mes
        df["date"] = pd.to_datetime(df["date"]).dt.date
        wrong_month = [d for d in df["date"].tolist() if (d.year != cmd.year or d.month != cmd.month)]
        if wrong_month:
            return UploadMonthlyMenuResult(
                status="error",
                message="El archivo contiene fechas fuera del mes/año indicado",
                preview_days=[],
                template_example=None
            )

        # 3) ¿existe menú actual?
        existing = await self.menu_repo.find_by_year_month(cmd.year, cmd.month)
        if existing:
            # devolvemos preview (conflict) para que el front confirme overwrite
            preview = [
                dict(date=str(r["date"]), breakfast=r["breakfast"], lunch=r["lunch"], dinner=r["dinner"])
                for _, r in df.iterrows()
            ]
            return UploadMonthlyMenuResult(
                status="conflict",
                message="Ya existe un menú para ese mes. ¿Deseas reemplazarlo?",
                preview_days=preview
            )

        # 4) crear menu y days (draft)
        menu = MonthlyMenu(
            id=None,
            year=cmd.year,
            month=cmd.month,
            status=MenuStatus.DRAFT,
            source_filename=cmd.filename,
            created_by=cmd.user_id
        )
        menu = await self.menu_repo.upsert(menu)

        days: List[MenuDay] = []
        for _, r in df.iterrows():
            d = MenuDay(
                id=None,
                menu_id=menu.id,
                date=r["date"],
                breakfast=str(r["breakfast"] or ""),
                lunch=str(r["lunch"] or ""),
                dinner=str(r["dinner"] or ""),
            )
            days.append(d)

        await self.day_repo.bulk_replace(menu.id, days)

        preview = [
            dict(date=str(d.date), breakfast=d.breakfast, lunch=d.lunch, dinner=d.dinner)
            for d in days
        ]
        return UploadMonthlyMenuResult("ok", "Menú cargado en borrador", preview)
