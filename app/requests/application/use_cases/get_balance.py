"""Query: Obtener saldo de vacaciones del año"""
from dataclasses import dataclass
from typing import Optional
from app.requests.application.ports.vacation_balance_repository import VacationBalanceRepository
from app.requests.domain.vacation_balance import VacationBalance

@dataclass
class GetBalanceCommand:
    user_id: str
    year: int

class GetBalanceUseCase:
    def __init__(self, balance_repository: VacationBalanceRepository):
        self.balance_repository = balance_repository

    async def execute(self, cmd: GetBalanceCommand) -> Optional[VacationBalance]:
        return await self.balance_repository.get_for_user_year(cmd.user_id, cmd.year)
