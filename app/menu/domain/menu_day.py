from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, Any

@dataclass
class MenuDay:
    id: Optional[str]
    menu_id: str
    date: date
    breakfast: str = ""
    lunch: str = ""
    dinner: str = ""
    is_holiday: bool = False
    nutrition_flags: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    def set_meal(self, meal_type: str, value: str) -> None:
        if meal_type == "breakfast":
            self.breakfast = value
        elif meal_type == "lunch":
            self.lunch = value
        elif meal_type == "dinner":
            self.dinner = value
        else:
            raise ValueError("Invalid meal_type")
        self.updated_at = datetime.utcnow()
