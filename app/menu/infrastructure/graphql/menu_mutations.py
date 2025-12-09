import strawberry
from typing import List
from datetime import date, datetime

from app.building_blocks.exceptions import (
    AuthenticationException,
    AuthorizationException,
)
from app.users.domain.user_role import UserRole

from app.menu.application.use_cases.upload_monthly_menu import (
    UploadMonthlyMenuUseCase,
    UploadMonthlyMenuCommand,
)
from app.menu.application.use_cases.confirm_overwrite import (
    ConfirmOverwriteUseCase,
    ConfirmOverwriteCommand,
)
from app.menu.application.use_cases.propose_menu_change import (
    ProposeMenuChangeUseCase,
    MenuChangeItem,
)
from app.menu.application.use_cases.review_menu_change import (
    ReviewMenuChangeUseCase,
    ReviewMenuChangeCommand,
)
from app.menu.domain.menu_enums import MealType

from .menu_inputs import (
    UploadMonthlyMenuInput,
    ProposeMenuChangeInput,
    ReviewMenuChangeInput,
)
from .menu_types import UploadMenuResponse, ConfirmOverwriteResponse, MenuChangeInfo


def _get_current_user(info):
    user = info.context.get("current_user")
    if not user:
        raise AuthenticationException("Debes estar autenticado")
    return user


def _require_role(user, allowed: List[UserRole]):
    if user.role not in allowed:
        raise AuthorizationException("No autorizado")



@strawberry.type
class MenuMutations:
    @strawberry.mutation
    async def upload_monthly_menu(
        self,
        info,
        input: UploadMonthlyMenuInput,
    ) -> UploadMenuResponse:
        """
        Sube y REEMPLAZA el menú mensual completo usando el formato plano
        (date, breakfast, lunch, dinner) del Excel/CSV.
        """
        user = _get_current_user(info)
        _require_role(user, [UserRole.NUTRITIONIST, UserRole.ADMIN])

        uc = UploadMonthlyMenuUseCase(
            info.context["monthly_menu_repository"],
            info.context["weekly_menu_repository"],
            info.context["daily_menu_repository"],
            info.context["meal_repository"],
            info.context["meal_component_repository"],
        )

        result = await uc.execute(
            UploadMonthlyMenuCommand(
                year=input.year,
                month=input.month,
                filename=input.filename,
                file_base64=input.file_base64,
            )
        )

        return UploadMenuResponse(
            status=result.get("status", "error"),
            message=result.get("message", ""),
            # Para mantener el contrato del tipo, devolvemos algo aunque
            # el use case no envíe un preview específico.
            preview=result.get("preview") or [],
        )

    @strawberry.mutation
    async def confirm_overwrite_menu(
        self,
        info,
        input: UploadMonthlyMenuInput,
    ) -> ConfirmOverwriteResponse:
        """
        Solo lee el archivo y devuelve un preview sin escribir en BD.
        Se usa antes de hacer el upload definitivo.
        """
        user = _get_current_user(info)
        _require_role(user, [UserRole.NUTRITIONIST, UserRole.ADMIN])

        uc = ConfirmOverwriteUseCase(
            info.context["monthly_menu_repository"],
            info.context["weekly_menu_repository"],
            info.context["daily_menu_repository"],
            info.context["meal_repository"],
            info.context["meal_component_repository"],
        )

        res = await uc.execute(
            ConfirmOverwriteCommand(
                year=input.year,
                month=input.month,
                filename=input.filename,
                file_base64=input.file_base64,
            )
        )

        return ConfirmOverwriteResponse(
            status=res.get("status", "error"),
            message=res.get("message", ""),
            preview=res.get("preview") or {},
        )

    @strawberry.mutation
    async def propose_menu_change(
        self,
        info,
        input: ProposeMenuChangeInput,
    ) -> List[MenuChangeInfo]:
        """
        El cocinero propone cambios puntuales a uno o varios días/comidas.
        Cada ítem sigue usando el nombre menu_day_id por compatibilidad con el
        frontend, pero internamente es el daily_menu_id.
        """
        user = _get_current_user(info)
        # Cocinero propone, admin también puede.
        _require_role(user, [UserRole.COOK, UserRole.ADMIN])

        uc = UploadMonthlyMenuUseCase(
            info.context["monthly_menu_repository"],
            info.context["weekly_menu_repository"],
            info.context["daily_menu_repository"],
            info.context["meal_repository"],
            info.context["meal_component_repository"],
            info.context["component_type_repository"],
        )

        items: List[MenuChangeItem] = []
        for it in input.items:
            items.append(
                MenuChangeItem(
                    menu_day_id=it.menu_day_id,  # es el daily_menu_id
                    day_date=it.day,
                    meal_type=MealType(it.meal_type),
                    new_value=it.new_value,
                    reason=it.reason,
                    emergency=it.emergency,
                )
            )

        reqs = await uc.execute(requested_by=user.id, items=items)

        return [
            MenuChangeInfo(
                id=r.id,
                date=r.day_date,
                meal_type=r.meal_type.value,
                old_value=r.old_value,
                new_value=r.new_value,
                status=r.status.value,
                requested_by=r.requested_by,
                decided_by=r.decided_by,
                decided_at=r.decided_at,
                notes=r.notes_from_decider,
                batch_id=r.batch_id,
            )
            for r in reqs
        ]

    @strawberry.mutation
    async def review_menu_change(
        self,
        info,
        input: ReviewMenuChangeInput,
    ) -> MenuChangeInfo:
        """
        Nutricionista/Admin aprueba o rechaza un cambio de menú.
        Si se aprueba, se aplica sobre los componentes del meal correspondiente.
        """
        user = _get_current_user(info)
        _require_role(user, [UserRole.NUTRITIONIST, UserRole.ADMIN])

        uc = ReviewMenuChangeUseCase(
            info.context["menu_change_repository"],
            info.context["daily_menu_repository"],
            info.context["meal_repository"],
            info.context["meal_component_repository"],
        )

        r = await uc.execute(
            ReviewMenuChangeCommand(
                change_id=input.change_id,
                decider_id=user.id,
                approve=input.approve,
                notes=input.notes,
            )
        )

        return MenuChangeInfo(
            id=r.id,
            date=r.day_date,
            meal_type=r.meal_type.value,
            old_value=r.old_value,
            new_value=r.new_value,
            status=r.status.value,
            requested_by=r.requested_by,
            decided_by=r.decided_by,
            decided_at=r.decided_at,
            notes=r.notes_from_decider,
            batch_id=r.batch_id,
        )
