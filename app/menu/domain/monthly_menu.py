from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .menu_enums import MenuStatus

@dataclass
class MonthlyMenu:
    id: Optional[str]
    year: int
    month: int
    status: MenuStatus = MenuStatus.DRAFT
    source_filename: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    def activate(self) -> None:
        self.status = MenuStatus.ACTIVE
        self.updated_at = datetime.utcnow()
