from __future__ import annotations

import strawberry
from datetime import date, datetime
from typing import Optional, List


# ======================
# TIPOS NUEVOS (sin enum)
# ======================


@strawberry.type
class MenuMealComponentInfo:
    """
    Componente individual dentro de una comida:
    Ej: BEBIDA CALIENTE, PLATO DE FONDO 1, GUARNICION 2, POSTRE, etc.
    """
    component_type: str
    dish_name: str
    calories: Optional[int]
    order: int


@strawberry.type
class MenuMealInfo:
    """
    Una comida del día con todos sus componentes.
    """
    meal_type: str  # "BREAKFAST", "LUNCH", "DINNER"
    total_kcal: Optional[int]
    components: List[MenuMealComponentInfo]


# ======================
# TIPOS EXISTENTES
# ======================


@strawberry.type
class MenuDayInfo:
    id: str
    date: date

    # Campos actuales que usa la app
    breakfast: str
    lunch: str
    dinner: str
    is_holiday: bool
    nutrition_flags: strawberry.scalars.JSON

    # NUEVO: detalle completo del día (desayuno, almuerzo y cena)
    meals: List[MenuMealInfo] = strawberry.field(default_factory=list)


@strawberry.type
class MonthlyMenuCalendar:
    year: int
    month: int
    days: List[MenuDayInfo]


@strawberry.type
class MenuChangeInfo:
    id: str
    date: date
    meal_type: str
    old_value: str
    new_value: str
    status: str
    requested_by: str
    decided_by: Optional[str]
    decided_at: Optional[datetime]
    notes: Optional[str]
    batch_id: Optional[str]


@strawberry.type
class UploadMenuResponse:
    status: str
    message: str
    preview: strawberry.scalars.JSON


@strawberry.type
class ConfirmOverwriteResponse:
    status: str
    message: str
    preview: strawberry.scalars.JSON


@strawberry.type
class ExportedFile:
    status: str
    filename: Optional[str] = None
    content_base64: Optional[str] = None
    message: Optional[str] = None
