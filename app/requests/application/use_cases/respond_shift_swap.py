"""Caso de uso: Responder intercambio (aceptar/rechazar) por el destinatario"""
from dataclasses import dataclass
from app.requests.application.ports.shift_swap_repository import ShiftSwapRepository
from app.requests.domain.request_status import SwapStatus
from app.building_blocks.exceptions import DomainException, NotFoundException, AuthorizationException

@dataclass
class RespondShiftSwapCommand:
    swap_id: str
    responder_id: str
    accept: bool
    note: str | None = None

class RespondShiftSwapUseCase:
    def __init__(self, swap_repository: ShiftSwapRepository):
        self.swap_repository = swap_repository

    async def execute(self, cmd: RespondShiftSwapCommand) -> dict:
        swap = await self.swap_repository.find_by_id(cmd.swap_id)
        if not swap:
            raise NotFoundException("Intercambio", cmd.swap_id)

        if swap.status != SwapStatus.PENDING:
            raise DomainException("Solo puedes responder intercambios en estado pending")

        if swap.target_user_id != cmd.responder_id:
            raise AuthorizationException("Solo el destinatario puede responder este intercambio")

        if cmd.accept:
            swap.accept()
            swap.status = SwapStatus.ACCEPTED
        else:
            swap.reject()
            swap.status = SwapStatus.REJECTED

        if cmd.note:
            swap.note = (swap.note or "") + f"\nRespuesta: {cmd.note}"

        saved = await self.swap_repository.save(swap)
        return {"success": True, "status": saved.status.value}
