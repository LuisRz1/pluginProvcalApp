"""Puerto para repositorio de saldos de vacaciones"""
from abc import ABC, abstractmethod
from typing import Optional
from app.requests.domain.vacation_balance import VacationBalance

class VacationBalanceRepository(ABC):
    """Contrato para persistencia/lectura del saldo de vacaciones"""

    @abstractmethod
    async def get_for_user_year(self, user_id: str, year: int) -> Optional[VacationBalance]:
        """Obtiene el saldo de vacaciones de un usuario para un año calendario"""

    @abstractmethod
    async def save(self, balance: VacationBalance) -> VacationBalance:
        """Guarda o actualiza el saldo de vacaciones"""
