"""Inputs GraphQL para asistencia"""
import strawberry
from typing import Optional
from datetime import datetime

@strawberry.input
class CheckInInput:
    latitude: float
    longitude: float
    accuracy: float = 10.0
    # Estos valores deberían venir de configuración del usuario/empresa
    workplace_latitude: float = -8.110336
    workplace_longitude: float = -79.028338
    workplace_radius_meters: float = 100.0

@strawberry.input
class CheckOutInput:
    latitude: float
    longitude: float
    accuracy: float = 10.0

@strawberry.input
class StartBreakInput:
    latitude: float
    longitude: float
    accuracy: float = 10.0

@strawberry.input
class EndBreakInput:
    latitude: float
    longitude: float
    accuracy: float = 10.0

@strawberry.input
class RegularizeAttendanceInput:
    attendance_id: str
    notes: str
    adjusted_check_in: Optional[datetime] = None
    adjusted_check_out: Optional[datetime] = None
