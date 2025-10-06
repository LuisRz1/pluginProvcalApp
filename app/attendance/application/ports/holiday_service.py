"""Puerto para servicio de días festivos"""
from abc import ABC, abstractmethod
from datetime import date

class HolidayService(ABC):

    @abstractmethod
    async def is_holiday(self, check_date: date) -> bool:
        """Verifica si una fecha es festiva"""


