"""Inputs GraphQL para solicitudes (time off y swap)"""
import strawberry
from typing import Optional
from datetime import datetime

@strawberry.input
class RequestTimeOffInput:
    type: str           # "vacation" | "permission"
    start_date: datetime
    end_date: datetime
    reason: Optional[str] = None

@strawberry.input
class CancelTimeOffInput:
    request_id: str

@strawberry.input
class ApproveTimeOffInput:
    request_id: str

@strawberry.input
class RejectTimeOffInput:
    request_id: str
    reason: str

@strawberry.input
class ProposeShiftSwapInput:
    requester_shift_id: str
    target_user_id: str
    target_shift_id: str
    note: Optional[str] = None

@strawberry.input
class RespondShiftSwapInput:
    swap_id: str
    accept: bool
    note: Optional[str] = None
