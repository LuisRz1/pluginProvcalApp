import strawberry
from typing import List, Optional
from datetime import date, datetime

from app.menu.application.use_cases.get_monthly_menu import (
    GetMonthlyMenuUseCase,
    GetMonthlyMenuQuery,
)
from app.menu.application.use_cases.get_menu_change_history import (
    GetMenuChangeHistoryUseCase,
    GetMenuChangeHistoryQuery,
)
from app.menu.application.use_cases.export_monthly_menu import ExportMonthlyMenuUseCase
from .menu_types import (
    MonthlyMenuCalendar,
    MenuDayInfo,
    MenuChangeInfo,
    ExportedFile,
    MenuMealInfo,
    MenuMealComponentInfo,
)


def _require_auth(info) -> None:
    if not info.context.get("current_user"):
        raise Exception("No autenticado")


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return date.fromisoformat(value)


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    # str(c.decided_at) en el use case devuelve ISO por defecto
    return datetime.fromisoformat(value)


@strawberry.type
class MenuQueries:
    @strawberry.field
    async def menu(self, info, year: int, month: int) -> Optional[MonthlyMenuCalendar]:
        """
        Devuelve el calendario mensual ya normalizado (daily_menus + meals +
        meal_components) empaquetado en la estructura plana que usa el frontend:
        breakfast / lunch / dinner por día, y además el detalle completo en 'meals'.
        """
        _require_auth(info)

        uc = GetMonthlyMenuUseCase(
            info.context["monthly_menu_repository"],
            info.context["weekly_menu_repository"],
            info.context["daily_menu_repository"],
            info.context["meal_repository"],
            info.context["meal_component_repository"],
        )
        rows = await uc.execute(GetMonthlyMenuQuery(year=year, month=month))

        if not rows:
            return None

        days: List[MenuDayInfo] = []

        for row in rows:
            # Detalle completo de comidas para el día (BREAKFAST/LUNCH/DINNER)
            meals_raw = row.get("meals") or []

            meals: List[MenuMealInfo] = []
            for m in meals_raw:
                components_raw = m.get("components") or []

                components: List[MenuMealComponentInfo] = [
                    MenuMealComponentInfo(
                        component_type=c.get("component_type") or "",
                        dish_name=c.get("dish_name") or "",
                        calories=c.get("calories"),
                        order=c.get("order") or 0,
                    )
                    for c in components_raw
                ]

                meals.append(
                    MenuMealInfo(
                        meal_type=m.get("meal_type") or "",
                        total_kcal=m.get("total_kcal"),
                        components=components,
                    )
                )

            days.append(
                MenuDayInfo(
                    id=row["id"],
                    date=date.fromisoformat(row["date"]),
                    breakfast=row["breakfast"],
                    lunch=row["lunch"],
                    dinner=row["dinner"],
                    is_holiday=row["is_holiday"],
                    nutrition_flags=row.get("nutrition_flags") or {},
                    meals=meals,
                )
            )

        return MonthlyMenuCalendar(year=year, month=month, days=days)

    @strawberry.field
    async def menu_change_history(
        self,
        info,
        year: int,
        month: int,
    ) -> List[MenuChangeInfo]:
        """
        Historial de cambios solicitados para el mes (para auditoría).
        """
        _require_auth(info)

        uc = GetMenuChangeHistoryUseCase(info.context["menu_change_repository"])
        data = await uc.execute(GetMenuChangeHistoryQuery(year=year, month=month))

        return [
            MenuChangeInfo(
                id=x["id"],
                date=_parse_date(x["date"]),
                meal_type=x["meal_type"],
                old_value=x["old_value"],
                new_value=x["new_value"],
                status=x["status"],
                requested_by=x["requested_by"],
                decided_by=x["decided_by"],
                decided_at=_parse_datetime(x["decided_at"]),
                notes=x["notes"],
                batch_id=x["batch_id"],
            )
            for x in data
        ]

    @strawberry.field
    async def export_monthly_menu(
        self,
        info,
        year: int,
        month: int,
    ) -> ExportedFile:
        """
        Exporta el menú mensual a un archivo (base64) usando el mismo formato
        plano que el Excel.
        """
        _require_auth(info)

        uc = ExportMonthlyMenuUseCase(
            info.context["monthly_menu_repository"],
            info.context["weekly_menu_repository"],
            info.context["daily_menu_repository"],
            info.context["meal_repository"],
            info.context["meal_component_repository"],
        )
        res = await uc.execute(year, month)

        return ExportedFile(
            status=res.get("status", "error"),
            filename=res.get("filename"),
            content_base64=res.get("content_base64"),
            message=res.get("message"),
        )
