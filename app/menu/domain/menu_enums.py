from enum import Enum

class MenuStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"

class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"

class ChangeStatus(str, Enum):
    PENDING = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EMERGENCY_APPLIED = "emergency_applied"
