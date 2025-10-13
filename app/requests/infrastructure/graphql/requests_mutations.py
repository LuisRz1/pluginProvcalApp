"""Mutations GraphQL para Requests"""
import strawberry
from strawberry.types import Info
from datetime import datetime

from app.building_blocks.exceptions import DomainException, AuthenticationException

from app.requests.infrastructure.graphql.requests_inputs import (
    RequestTimeOffInput, CancelTimeOffInput,
    ApproveTimeOffInput, RejectTimeOffInput,
    ProposeShiftSwapInput, RespondShiftSwapInput
)
from app.requests.infrastructure.graphql.requests_types import (
    RequestTimeOffResponse, CancelTimeOffResponse,
    ApproveTimeOffResponse, RejectTimeOffResponse,
    ProposeShiftSwapResponse, RespondShiftSwapResponse,
    TimeOffRequestInfo, ShiftSwapInfo
)

# Use cases (paso 4)
from app.requests.application.use_cases.request_time_off import (
    RequestTimeOffUseCase, RequestTimeOffCommand
)
from app.requests.application.use_cases.cancel_time_off import (
    CancelTimeOffUseCase, CancelTimeOffCommand
)
from app.requests.application.use_cases.approve_time_off import (
    ApproveTimeOffUseCase, ApproveTimeOffCommand
)
from app.requests.application.use_cases.reject_time_off import (
    RejectTimeOffUseCase, RejectTimeOffCommand
)
from app.requests.application.use_cases.propose_shift_swap import (
    ProposeShiftSwapUseCase, ProposeShiftSwapCommand
)
from app.requests.application.use_cases.respond_shift_swap import (
    RespondShiftSwapUseCase, RespondShiftSwapCommand
)


@strawberry.type
class RequestsMutations:

    # ----- Time off -----
    @strawberry.mutation
    async def request_time_off(self, info: Info, input: RequestTimeOffInput) -> RequestTimeOffResponse:
        try:
            if not info.context.get("current_user"):
                raise AuthenticationException("Debes estar autenticado")

            user = info.context["current_user"]

            cmd = RequestTimeOffCommand(
                user_id=user.id,
                type=input.type,
                start_date=input.start_date.date(),
                end_date=input.end_date.date(),
                reason=input.reason
            )

            use_case = RequestTimeOffUseCase(
                time_off_repository=info.context["time_off_repository"],
                vacation_balance_repository=info.context["vacation_balance_repository"],
                user_repository=info.context["user_repository"]
            )
            result = await use_case.execute(cmd)

            req = result["request"]
            return RequestTimeOffResponse(
                success=True,
                message=result["message"],
                request=TimeOffRequestInfo(
                    id=req.id,
                    user_id=req.user_id,
                    type=req.type.value,
                    status=req.status.value,
                    start_date=req.start_date,
                    end_date=req.end_date,
                    days_requested=req.days_requested,
                    reason=req.reason,
                    created_at=req.created_at,
                    updated_at=req.updated_at
                )
            )
        except (DomainException, AuthenticationException) as e:
            return RequestTimeOffResponse(success=False, message=str(e))

    @strawberry.mutation
    async def cancel_time_off(self, info: Info, input: CancelTimeOffInput) -> CancelTimeOffResponse:
        try:
            if not info.context.get("current_user"):
                raise AuthenticationException("Debes estar autenticado")

            user = info.context["current_user"]
            cmd = CancelTimeOffCommand(request_id=input.request_id, user_id=user.id)
            use_case = CancelTimeOffUseCase(
                time_off_repository=info.context["time_off_repository"],
                vacation_balance_repository=info.context["vacation_balance_repository"]
            )
            result = await use_case.execute(cmd)
            return CancelTimeOffResponse(success=True, message=result["message"])
        except (DomainException, AuthenticationException) as e:
            return CancelTimeOffResponse(success=False, message=str(e))

    @strawberry.mutation
    async def approve_time_off(self, info: Info, input: ApproveTimeOffInput) -> ApproveTimeOffResponse:
        try:
            user = info.context.get("current_user")
            if not user:
                raise AuthenticationException("Debes estar autenticado")

            # Autorización admin (igual a attendance.regularize)
            from app.users.domain.user_role import UserRole
            if user.role != UserRole.ADMIN:
                raise AuthenticationException("Solo administradores pueden aprobar solicitudes")

            cmd = ApproveTimeOffCommand(request_id=input.request_id, admin_id=user.id)
            use_case = ApproveTimeOffUseCase(
                time_off_repository=info.context["time_off_repository"],
                vacation_balance_repository=info.context["vacation_balance_repository"]
            )
            result = await use_case.execute(cmd)
            return ApproveTimeOffResponse(success=True, message=result["message"])
        except (DomainException, AuthenticationException) as e:
            return ApproveTimeOffResponse(success=False, message=str(e))

    @strawberry.mutation
    async def reject_time_off(self, info: Info, input: RejectTimeOffInput) -> RejectTimeOffResponse:
        try:
            user = info.context.get("current_user")
            if not user:
                raise AuthenticationException("Debes estar autenticado")

            from app.users.domain.user_role import UserRole
            if user.role != UserRole.ADMIN:
                raise AuthenticationException("Solo administradores pueden rechazar solicitudes")

            cmd = RejectTimeOffCommand(
                request_id=input.request_id,
                admin_id=user.id,
                reason=input.reason
            )
            use_case = RejectTimeOffUseCase(
                time_off_repository=info.context["time_off_repository"],
                vacation_balance_repository=info.context["vacation_balance_repository"]
            )
            result = await use_case.execute(cmd)
            return RejectTimeOffResponse(success=True, message=result["message"])
        except (DomainException, AuthenticationException) as e:
            return RejectTimeOffResponse(success=False, message=str(e))

    # ----- Shift swap -----
    @strawberry.mutation
    async def propose_shift_swap(self, info: Info, input: ProposeShiftSwapInput) -> ProposeShiftSwapResponse:
        try:
            if not info.context.get("current_user"):
                raise AuthenticationException("Debes estar autenticado")
            user = info.context["current_user"]

            cmd = ProposeShiftSwapCommand(
                requester_id=user.id,
                target_user_id=input.target_user_id,
                requester_shift_id=input.requester_shift_id,
                target_shift_id=input.target_shift_id,
                note=input.note
            )
            use_case = ProposeShiftSwapUseCase(
                swap_repository=info.context["swap_repository"],
                user_repository=info.context["user_repository"],
                work_schedule_repository=info.context["work_schedule_repository"]
            )
            result = await use_case.execute(cmd)

            s = result["swap"]
            return ProposeShiftSwapResponse(
                success=True,
                message=result["message"],
                swap=ShiftSwapInfo(
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
            )
        except (DomainException, AuthenticationException) as e:
            return ProposeShiftSwapResponse(success=False, message=str(e))

    @strawberry.mutation
    async def respond_shift_swap(self, info: Info, input: RespondShiftSwapInput) -> RespondShiftSwapResponse:
        try:
            if not info.context.get("current_user"):
                raise AuthenticationException("Debes estar autenticado")
            user = info.context["current_user"]

            cmd = RespondShiftSwapCommand(
                swap_id=input.swap_id,
                responder_id=user.id,
                accept=input.accept,
                note=input.note
            )
            use_case = RespondShiftSwapUseCase(
                swap_repository=info.context["swap_repository"],
                user_repository=info.context["user_repository"],
                work_schedule_repository=info.context["work_schedule_repository"]
            )
            result = await use_case.execute(cmd)
            s = result["swap"]
            return RespondShiftSwapResponse(
                success=True,
                message=result["message"],
                swap=ShiftSwapInfo(
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
            )
        except (DomainException, AuthenticationException) as e:
            return RespondShiftSwapResponse(success=False, message=str(e))
