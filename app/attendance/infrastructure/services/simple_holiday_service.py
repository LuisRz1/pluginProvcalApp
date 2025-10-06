"""Implementación simple del servicio de días festivos"""
from datetime import date
from app.attendance.application.ports.holiday_service import HolidayService

class SimpleHolidayService(HolidayService):
    """
    Implementación simple con días festivos de Perú hardcodeados.
    En producción, esto debería venir de una base de datos o API.
    """

    # Días festivos fijos de Perú 2025
    FIXED_HOLIDAYS = [
        (1, 1),   # Año Nuevo
        (5, 1),   # Día del Trabajo
        (6, 29),  # San Pedro y San Pablo
        (7, 28),  # Día de la Independencia
        (7, 29),  # Día de la Independencia
        (8, 30),  # Santa Rosa de Lima
        (10, 8),  # Combate de Angamos
        (11, 1),  # Todos los Santos
        (12, 8),  # Inmaculada Concepción
        (12, 25), # Navidad
    ]

    async def is_holiday(self, check_date: date) -> bool:
        """Verifica si una fecha es festiva"""
        # Verificar festivos fijos
        month_day = (check_date.month, check_date.day)
        if month_day in self.FIXED_HOLIDAYS:
            return True

        # Aquí podrías agregar lógica para festivos móviles
        # (Jueves Santo, Viernes Santo, etc.)

        return False