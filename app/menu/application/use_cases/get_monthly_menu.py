from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from app.menu.application.ports.monthly_menu_repository import MonthlyMenuRepository
from app.menu.application.ports.weekly_menu_repository import WeeklyMenuRepository
from app.menu.application.ports.daily_menu_repository import DailyMenuRepository
from app.menu.application.ports.meal_repository import MealRepository
from app.menu.application.ports.meal_component_repository import MealComponentRepository
from app.menu.domain.menu_enums import MealType


@dataclass(frozen=True)
class GetMonthlyMenuQuery:
    year: int
    month: int


class GetMonthlyMenuUseCase:
    """
    Devuelve una lista de días con labels (breakfast/lunch/dinner) y,
    además, el detalle completo de cada comida (meals) para el FE.
    """
    def __init__(
        self,
        menu_repo: MonthlyMenuRepository,
        weekly_repo: WeeklyMenuRepository,
        day_repo: DailyMenuRepository,
        meal_repo: MealRepository,
        meal_component_repo: MealComponentRepository,
    ):
        self.menu_repo = menu_repo
        self.weekly_repo = weekly_repo
        self.day_repo = day_repo
        self.meal_repo = meal_repo
        self.meal_component_repo = meal_component_repo

    async def _meal_text(self, daily_id: str, mt: MealType) -> str:
        """
        Versión simplificada para compatibilidad con el FE actual:
        devuelve solo el nombre del primer componente de la comida.
        """
        m = await self.meal_repo.find_by_daily_and_type(daily_id, mt)
        if not m:
            return ""
        comps = await self.meal_component_repo.list_by_meal(str(m.id))
        return comps[0].dish_name if comps else ""

    async def _meal_detail(self, daily_id: str, mt: MealType) -> Optional[Dict[str, Any]]:
        """
        Construye el detalle completo de una comida:
        - meal_type: "BREAKFAST" | "LUNCH" | "DINNER"
        - total_kcal: TOTAL Kcal de la sección
        - components: lista de componentes con tipo, plato, kcal y orden
        """
        m = await self.meal_repo.find_by_daily_and_type(daily_id, mt)
        if not m:
            return None

        comps = await self.meal_component_repo.list_by_meal(str(m.id))

        components_payload: List[Dict[str, Any]] = []
        for c in comps:
            # Se asume que meal_component tiene relación component_type con atributo name
            component_type_name = ""
            if getattr(c, "component_type", None) is not None:
                component_type_name = getattr(c.component_type, "name", "") or ""

            components_payload.append(
                dict(
                    component_type=component_type_name,
                    dish_name=c.dish_name,
                    calories=c.calories,
                    order=c.order_position,
                )
            )

        # Si por algún motivo no hay componentes, no devolvemos nada
        if not components_payload:
            return None

        return dict(
            meal_type=mt.name,          # "BREAKFAST", "LUNCH", "DINNER"
            total_kcal=m.total_kcal,    # puede ser None si no se leyó TOTAL Kcal en el Excel
            components=components_payload,
        )

    async def execute(self, q: GetMonthlyMenuQuery) -> List[Dict[str, Any]]:
        menu = await self.menu_repo.find_by_year_month(q.year, q.month)
        if not menu:
            return []

        weeks = await self.weekly_repo.list_by_month(str(menu.id))
        days = []
        for w in weeks:
            days.extend(await self.day_repo.list_by_week(str(w.id)))
        # ordenar por fecha
        days.sort(key=lambda d: d.date)

        out: List[Dict[str, Any]] = []
        for d in days:
            day_id = str(d.id)

            # Campos simples para compatibilidad con el FE actual
            b = await self._meal_text(day_id, MealType.BREAKFAST)
            l = await self._meal_text(day_id, MealType.LUNCH)
            dn = await self._meal_text(day_id, MealType.DINNER)

            # NUEVO: detalle completo de cada comida
            meals: List[Dict[str, Any]] = []
            for mt in (MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER):
                detail = await self._meal_detail(day_id, mt)
                if detail is not None:
                    meals.append(detail)

            out.append(
                dict(
                    id=day_id,
                    date=str(d.date),
                    breakfast=b,
                    lunch=l,
                    dinner=dn,
                    is_holiday=d.is_holiday,
                    nutrition_flags={},  # se deja vacío para compatibilidad
                    meals=meals,         # NUEVO: usado por MenuDayInfo.meals
                )
            )
        return out
