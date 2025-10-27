import strawberry
from datetime import date
from typing import Optional, List

@strawberry.input
class UploadMonthlyMenuInput:
    year: int
    month: int
    filename: str
    file_base64: str  # Front enviará base64 del .xlsx

@strawberry.input
class MenuChangeItemInput:
    menu_day_id: str
    day: date
    meal_type: str      # "breakfast" | "lunch" | "dinner"
    new_value: str
    reason: str
    emergency: bool = False

@strawberry.input
class ProposeMenuChangeInput:
    items: List[MenuChangeItemInput]

@strawberry.input
class ReviewMenuChangeInput:
    change_id: str
    approve: bool
    notes: Optional[str] = None
