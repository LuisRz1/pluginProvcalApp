"""Tipos GraphQL para Requests (time off, balances, shift swaps)"""
import strawberry
from typing import Optional, List
from datetime import datetime, date

# ----- Infos -----
@strawberry.type
class TimeOffRequestInfo:
    id: str
    user_id: str
    type: str
    status: str
    start_date: date
    end_date: date
    days_requested: int
    reason: Optional[str]
    created_at: datetime
    updated_at: datetime

@strawberry.type
class VacationBalanceInfo:
    user_id: str
    year: int
    total_days: int
    consumed_days: int
    carried_over_days: int
    available_days: int

@strawberry.type
class ShiftSwapInfo:
    id: str
    requester_id: str
    target_user_id: str
    requester_shift_id: str
    target_shift_id: str
    status: str
    note: Optional[str]
    created_at: datetime
    updated_at: datetime
    responded_at: Optional[datetime]

# ----- Responses (mismo patrón que attendance) -----
@strawberry.type
class RequestTimeOffResponse:
    success: bool
    message: str
    request: Optional[TimeOffRequestInfo] = None

@strawberry.type
class CancelTimeOffResponse:
    success: bool
    message: str

@strawberry.type
class ApproveTimeOffResponse:
    success: bool
    message: str

@strawberry.type
class RejectTimeOffResponse:
    success: bool
    message: str

@strawberry.type
class ProposeShiftSwapResponse:
    success: bool
    message: str
    swap: Optional[ShiftSwapInfo] = None

@strawberry.type
class RespondShiftSwapResponse:
    success: bool
    message: str
    swap: Optional[ShiftSwapInfo] = None

# ----- Query result lists -----
@strawberry.type
class MyTimeOffRequestsResult:
    items: List[TimeOffRequestInfo]

@strawberry.type
class MyShiftSwapsResult:
    items: List[ShiftSwapInfo]

@strawberry.type
class MyVacationBalanceResult:
    success: bool
    message: str
    balance: Optional[VacationBalanceInfo] = None
