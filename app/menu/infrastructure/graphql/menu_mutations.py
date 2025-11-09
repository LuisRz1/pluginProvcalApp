import base64
import strawberry
from typing import List
from datetime import date, datetime

from app.building_blocks.exceptions import AuthenticationException, AuthorizationException
from app.users.domain.user import UserRole

from app.menu.application.use_cases.upload_monthly_menu import UploadMonthlyMenuUseCase, UploadMonthlyMenuCommand
from app.menu.application.use_cases.confirm_overwrite import ConfirmOverwriteUseCase, ConfirmOverwriteCommand
from app.menu.application.use_cases.propose_menu_change import ProposeMenuChangeUseCase, ProposeMenuChangeCommand, MenuChangeItem
from app.menu.application.use_cases.review_menu_change import ReviewMenuChangeUseCase, ReviewMenuChangeCommand
from app.menu.domain.menu_enums import MealType

from .menu_inputs import UploadMonthlyMenuInput, ProposeMenuChangeInput, ReviewMenuChangeInput
from .menu_types import UploadMenuResponse, ConfirmOverwriteResponse, MenuChangeInfo

def _require_roles(info, allowed: set[str]):
    user = info.context.get("current_user")
    if not user or user.role.value not in allowed:
        raise Exception("No autorizado")

@strawberry.type
class MenuMutations:

    @strawberry.mutation
    async def upload_monthly_menu(self, info, input: UploadMonthlyMenuInput) -> UploadMenuResponse:
        user = info.context["current_user"]
        if not user:
            raise AuthenticationException("Debes estar autenticado")
        if user.role not in (UserRole.NUTRICIONISTA, UserRole.ADMIN):
            raise AuthorizationException("No autorizado")

        file_bytes = base64.b64decode(input.file_base64.encode("utf-8"))
        result = await UploadMonthlyMenuUseCase(
            info.context["monthly_menu_repository"],
            info.context["menu_day_repository"]
        ).execute(UploadMonthlyMenuCommand(
            user_id=user.id,
            filename=input.filename,
            file_bytes=file_bytes,
            year=input.year,
            month=input.month
        ))

        return UploadMenuResponse(status=result.status, message=result.message, preview=result.preview_days)

    @strawberry.mutation
    async def confirm_overwrite_menu(self, info, input: UploadMonthlyMenuInput) -> ConfirmOverwriteResponse:
        user = info.context["current_user"]
        if not user:
            raise AuthenticationException("Debes estar autenticado")
        if user.role not in (UserRole.NUTRICIONISTA, UserRole.ADMIN):
            raise AuthorizationException("No autorizado")

        file_bytes = base64.b64decode(input.file_base64.encode("utf-8"))
        result = await ConfirmOverwriteUseCase(
            info.context["monthly_menu_repository"],
            info.context["menu_day_repository"]
        ).execute(ConfirmOverwriteCommand(
            user_id=user.id,
            filename=input.filename,
            file_bytes=file_bytes,
            year=input.year,
            month=input.month
        ))

        return ConfirmOverwriteResponse(status=result.status, message=result.message, preview=result.days)

    @strawberry.mutation
    async def propose_menu_change(self, info, input: ProposeMenuChangeInput) -> List[MenuChangeInfo]:
        user = info.context["current_user"]
        if not user:
            raise AuthenticationException("Debes estar autenticado")
        if user.role not in (UserRole.NUTRICIONISTA, UserRole.ADMIN):
            raise AuthorizationException("No autorizado")

        items = [
            MenuChangeItem(
                menu_day_id=i.menu_day_id,
                day_date=i.day,
                meal_type=MealType(i.meal_type),
                new_value=i.new_value,
                reason=i.reason,
                emergency=i.emergency
            )
            for i in input.items
        ]

        reqs = await ProposeMenuChangeUseCase(
            info.context["menu_change_repository"],
            info.context["menu_day_repository"]
        ).execute(ProposeMenuChangeCommand(
            requester_id=user.id,
            items=items
        ))

        return [
            MenuChangeInfo(
                id=r.id, date=r.day_date, meal_type=r.meal_type.value,
                old_value=r.old_value, new_value=r.new_value,
                status=r.status.value, requested_by=r.requested_by,
                decided_by=r.decided_by, decided_at=r.decided_at,
                notes=r.notes_from_decider, batch_id=r.batch_id
            ) for r in reqs
        ]

    @strawberry.mutation
    async def review_menu_change(self, info, input: ReviewMenuChangeInput) -> MenuChangeInfo:
        user = info.context["current_user"]
        if not user:
            raise AuthenticationException("Debes estar autenticado")
        if user.role not in (UserRole.CHEF, UserRole.ADMIN):
            raise AuthorizationException("No autorizado")

        r = await ReviewMenuChangeUseCase(
            info.context["menu_change_repository"],
            info.context["menu_day_repository"]
        ).execute(ReviewMenuChangeCommand(
            change_id=input.change_id,
            decider_id=user.id,
            approve=input.approve,
            notes=input.notes
        ))

        return MenuChangeInfo(
            id=r.id, date=r.day_date, meal_type=r.meal_type.value,
            old_value=r.old_value, new_value=r.new_value,
            status=r.status.value, requested_by=r.requested_by,
            decided_by=r.decided_by, decided_at=r.decided_at,
            notes=r.notes_from_decider, batch_id=r.batch_id
        )
