"""Query: Listar mis intercambios de turnos"""
from dataclasses import dataclass
from typing import List
from app.requests.application.ports.shift_swap_repository import ShiftSwapRepository
from app.requests.domain.shift_swap_request import ShiftSwapRequest

@dataclass
class ListMySwapsCommand:
    user_id: str
    limit: int = 50

class ListMySwapsUseCase:
    def __init__(self, swap_repository: ShiftSwapRepository):
        self.swap_repository = swap_repository

    async def execute(self, cmd: ListMySwapsCommand) -> List[ShiftSwapRequest]:
        return await self.swap_repository.find_my_swaps(cmd.user_id, cmd.limit)
