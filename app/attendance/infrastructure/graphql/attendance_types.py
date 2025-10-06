"""Tipos GraphQL para asistencia"""
import strawberry
from typing import Optional, List
from datetime import datetime

@strawberry.type
class GeolocationInfo:
    latitude: float
    longitude: float
    accuracy: float

@strawberry.type
class BreakPeriodInfo:
    id: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[int]
    status: str
    is_exceeded: bool

@strawberry.type
class AttendanceInfo:
    id: str
    user_id: str
    date: datetime
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    status: str
    type: str
    is_late: bool
    late_minutes: int
    total_work_hours: Optional[float]
    break_periods: List[BreakPeriodInfo]
    requires_regularization: bool

@strawberry.type
class CheckInResponse:
    success: bool
    message: str
    attendance_id: Optional[str]
    check_in_time: Optional[datetime]
    is_late: bool
    late_minutes: int
    is_holiday: bool

@strawberry.type
class CheckOutResponse:
    success: bool
    message: str
    attendance_id: str
    check_out_time: datetime
    total_work_hours: float
    no_breaks_registered: bool

@strawberry.type
class StartBreakResponse:
    success: bool
    message: str
    break_id: Optional[str]
    start_time: datetime
    allowed_duration_minutes: int

@strawberry.type
class EndBreakResponse:
    success: bool
    message: str
    end_time: datetime
    duration_minutes: int
    is_exceeded: bool

@strawberry.type
class RegularizeAttendanceResponse:
    success: bool
    message: str