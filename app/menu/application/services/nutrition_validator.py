# app/menu/application/services/nutrition_validator.py
from typing import List
from app.menu.domain.menu_day import MenuDay
from app.menu.application.ports.menu_day_repository import MenuDayRepository

class SimpleNutritionValidator:
    """
    Validador simple: marca banderas si alguna comida viene vacía.
    Luego puedes cambiarlo por uno que consulte requerimientos reales.
    """
    async def validate_menu_days(self, days: List[MenuDay], repo: MenuDayRepository):
        for day in days:
            flags = {}
            if not day.breakfast:
                flags["breakfast"] = "empty"
            if not day.lunch:
                flags["lunch"] = "empty"
            if not day.dinner:
                flags["dinner"] = "empty"

            # si hay alguna bandera, la guardamos
            if flags:
                day.nutrition_flags = flags
                await repo.save(day)
