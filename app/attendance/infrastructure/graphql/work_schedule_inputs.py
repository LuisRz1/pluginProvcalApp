"""Inputs GraphQL para horarios"""
import strawberry
from typing import List, Optional
from datetime import date, time

@strawberry.input
class AssignWorkScheduleInput:
    user_id: str
    shift_type: str  # "morning", "afternoon", "night", "full_day", "custom"
    start_time: time
    end_time: time
    working_days: List[int]  # [0,1,2,3,4] = Lunes a Viernes
    late_tolerance_minutes: int = 15
    break_duration_minutes: int = 30
    effective_from: date = date.today()
    notes: Optional[str] = None

# Los morning deberian asignarse de 09:00 a 13:00 y de 14:00 a 18:00
# Los afternoon deberian asignarse de 14:00 a 18:00 y de 19:00 a 23:00
# Los night deberian asignarse de 22:00 a 06:00
# Los full_day deberian asignarse de 09:00 a 18:00
# Los custom pueden ser cualquier horario definido por el usuario