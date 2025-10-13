"""Queries GraphQL para Requests"""
import strawberry
from strawberry.types import Info
from datetime import datetime
from app.requests.infrastructure.graphql.requests_types import (
    MyTimeOffRequestsResult, MyShiftSwapsResult, MyVacationBalanceResult,
    TimeOffRequestInfo, ShiftSwapInfo, VacationBalanceInfo
)

@strawberry.type
class RequestsQueries:

    @strawberry.field
    async def my_time_off_requests(self, info: Info, limit: int = 30) -> MyTimeOffRequestsResult:
        if not info.context.get("current_user"):
            raise Exception("Debes estar autenticado")
        user = info.context["current_user"]

        # use case simple o directo al repo:
        items = await info.context["time_off_repository"].find_by_user(user.id, limit=limit)

        return MyTimeOffRequestsResult(
            items=[
                TimeOffRequestInfo(
                    id=i.id,
                    user_id=i.user_id,
                    type=i.type.value,
                    status=i.status.value,
                    start_date=i.start_date,
                    end_date=i.end_date,
                    days_requested=i.days_requested,
                    reason=i.reason,
                    created_at=i.created_at,
                    updated_at=i.updated_at
                )
                for i in items
            ]
        )

    @strawberry.field
    async def my_shift_swaps(self, info: Info, limit: int = 30) -> MyShiftSwapsResult:
        if not info.context.get("current_user"):
            raise Exception("Debes estar autenticado")
        user = info.context["current_user"]

        items = await info.context["swap_repository"].find_my_swaps(user.id, limit=limit)

        return MyShiftSwapsResult(
            items=[
                ShiftSwapInfo(
                    id=s.id,
                    requester_id=s.requester_id,
                    target_user_id=s.target_user_id,
                    requester_shift_id=s.requester_shift_id,
                    target_shift_id=s.target_shift_id,
                    status=s.status.value,
                    note=s.note,
                    created_at=s.created_at,
                    updated_at=s.updated_at,
                    responded_at=s.responded_at
                )
                for s in items
            ]
        )

    @strawberry.field
    async def my_vacation_balance(self, info: Info, year: int | None = None) -> MyVacationBalanceResult:
        if not info.context.get("current_user"):
            raise Exception("Debes estar autenticado")
        user = info.context["current_user"]

        # Año por defecto: actual (Perú / tz no afecta al año civil)
        if year is None:
            year = datetime.now().year

        balance = await info.context["vacation_balance_repository"].get_for_user_year(user.id, year)
        if not balance:
            return MyVacationBalanceResult(success=False, message="No hay saldo para el año indicado")

        return MyVacationBalanceResult(
            success=True,
            message="OK",
            balance=VacationBalanceInfo(
                user_id=balance.user_id,
                year=balance.year,
                total_days=balance.total_days,
                consumed_days=balance.consumed_days,
                carried_over_days=balance.carried_over_days,
                available_days=balance.available_days()
            )
        )
