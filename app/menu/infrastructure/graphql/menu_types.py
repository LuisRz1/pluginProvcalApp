import strawberry
from datetime import date, datetime
from typing import Optional, List, Dict, Any

@strawberry.type
class MenuDayInfo:
    id: str
    date: date
    breakfast: str
    lunch: str
    dinner: str
    is_holiday: bool
    nutrition_flags: strawberry.scalars.JSON

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
