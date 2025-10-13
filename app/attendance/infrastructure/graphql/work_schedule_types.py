"""Tipos GraphQL para horarios de trabajo"""
from typing import List, Optional
from datetime import date
import strawberry

@strawberry.type
class WorkScheduleInfo:
    id: str
    user_id: str
    shift_type: str
    start_time: str  # "09:00"
    end_time: str    # "18:00"
    working_days_names: List[str]  # ["Lunes", "Martes", ...]
    late_tolerance_minutes: int
    break_duration_minutes: int
    total_hours_per_day: float
    is_active: bool
    effective_from: date
    effective_until: Optional[date]
    notes: Optional[str]

@strawberry.type
class AssignScheduleResponse:
    success: bool
    message: str
    schedule: Optional[WorkScheduleInfo]
