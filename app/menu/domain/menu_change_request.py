from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from .menu_enums import MealType, ChangeStatus

@dataclass
class MenuChangeRequest:
    id: Optional[str]
    daily_menu_id: str
    day_date: date
    meal_type: MealType
    old_value: str
    new_value: str
    reason: str
    status: ChangeStatus = ChangeStatus.PENDING
    requested_by: str = ""
    decided_by: Optional[str] = None
    decided_at: Optional[datetime] = None
    notes_from_decider: Optional[str] = None
    batch_id: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    def approve(self, decider_id: str) -> None:
        if self.status != ChangeStatus.PENDING:
            raise ValueError("Solo se puede aprobar cambios en estado pendiente")
        self.status = ChangeStatus.APPROVED
        self.decided_by = decider_id
        self.decided_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def reject(self, decider_id: str, notes: Optional[str] = None) -> None:
        if self.status != ChangeStatus.PENDING:
            raise ValueError("Solo se puede rechazar cambios en estado pendiente")
        self.status = ChangeStatus.REJECTED
        self.decided_by = decider_id
        self.decided_at = datetime.utcnow()
        self.notes_from_decider = notes
        self.updated_at = datetime.utcnow()

    def mark_emergency_applied(self) -> None:
        self.status = ChangeStatus.EMERGENCY_APPLIED
        self.updated_at = datetime.utcnow()
