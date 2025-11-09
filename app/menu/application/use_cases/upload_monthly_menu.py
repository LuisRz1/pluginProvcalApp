import base64
import csv
import io
import uuid
from dataclasses import dataclass
from datetime import date, datetime
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
    def __init__(
        self,
        monthly_repo: MonthlyMenuRepository,
        menu_day_repo: MenuDayRepository,
        holiday_service=None,              # ← nuevo
        nutrition_validator=None           # ← lo usaremos en el punto 2
    ):
        self.monthly_repo = monthly_repo
        self.menu_day_repo = menu_day_repo
        self.holiday_service = holiday_service
        self.nutrition_validator = nutrition_validator

    async def execute(self, year: int, month: int, filename: str, file_base64: str):
        # 1. decodificar archivo
        try:
            raw = base64.b64decode(file_base64)
        except Exception:
            return {
                "status": "error",
                "message": "El archivo no está en base64 válido"
            }

        # 2. parsear CSV/XLSX-convertido-a-CSV (tú ya lo trabajabas así)
        # asumimos que llega como CSV para simplificar
        csv_buffer = io.StringIO(raw.decode("utf-8"))
        reader = csv.DictReader(csv_buffer)
        cols = reader.fieldnames or []

        missing = [c for c in REQUIRED_COLUMNS if c not in cols]
        if missing:
            return {
                "status": "error",
                "message": f"Faltan columnas: {', '.join(missing)}",
                "expected_columns": REQUIRED_COLUMNS
            }

        # 3. ¿ya existe menú para ese mes?
        existing = await self.monthly_repo.find_by_year_month(year, month)
        if existing:
            # devolvemos preview pero NO pisamos todavía
            preview_days = []
            csv_buffer.seek(0)
            next(reader)  # saltar header
            csv_buffer.seek(0)
            reader = csv.DictReader(csv_buffer)
            for row in reader:
                preview_days.append({
                    "date": row["date"],
                    "breakfast": row["breakfast"],
                    "lunch": row["lunch"],
                    "dinner": row["dinner"],
                })
            return {
                "status": "conflict",
                "message": "Ya existe un menú para este mes. Confirme sobrescritura.",
                "preview_days": preview_days
            }

        # 4. crear menú mensual
        monthly = MonthlyMenu.create(year=year, month=month, source_filename=filename)
        monthly = await self.monthly_repo.upsert(monthly)

        # 5. crear días
        days: List[MenuDay] = []
        csv_buffer.seek(0)
        reader = csv.DictReader(csv_buffer)
        for row in reader:
            day_date = datetime.strptime(row["date"], "%Y-%m-%d").date()
            is_holiday = False
            if self.holiday_service is not None:
                # si tu holiday_service tiene otra firma, la ajustas aquí
                is_holiday = await self.holiday_service.is_holiday(day_date)

            day = MenuDay.create(
                menu_id=str(monthly.id),
                date=day_date,
                breakfast=row["breakfast"],
                lunch=row["lunch"],
                dinner=row["dinner"],
                is_holiday=is_holiday,
            )
            days.append(day)

        # 6. guardar días
        await self.menu_day_repo.bulk_replace(str(monthly.id), days)

        # 7. opcional: correr validación nutricional automática
        if self.nutrition_validator is not None:
            await self.nutrition_validator.validate_menu_days(days, self.menu_day_repo)

        return {
            "status": "ok",
            "message": "Menú mensual cargado correctamente",
            "menu_id": str(monthly.id)
        }