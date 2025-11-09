from dataclasses import dataclass
from datetime import datetime, timezone
from app.requests.application.ports.shift_swap_repository import ShiftSwapRepository
from app.requests.application.ports.work_schedule_repository import WorkScheduleRepository
from app.users.application.ports.user_repository import UserRepository
from app.requests.domain.request_status import SwapStatus
from app.building_blocks.exceptions import DomainException, NotFoundException, AuthorizationException

@dataclass
class RespondShiftSwapCommand:
    swap_id: str
    responder_id: str
    accept: bool
    note: str | None = None

class RespondShiftSwapUseCase:
    def __init__(
        self,
        swap_repository: ShiftSwapRepository,
        user_repository: UserRepository,
        work_schedule_repository: WorkScheduleRepository,
    ):
        self.swap_repository = swap_repository
        self.user_repository = user_repository
        self.work_schedule_repository = work_schedule_repository

    async def execute(self, cmd: RespondShiftSwapCommand) -> dict:
        swap = await self.swap_repository.find_by_id(cmd.swap_id)
        if not swap:
            raise NotFoundException("Intercambio", cmd.swap_id)

        if swap.status != SwapStatus.PENDING:
            raise DomainException("Solo puedes responder intercambios en estado pending")

        if swap.target_user_id != cmd.responder_id:
            raise AuthorizationException("Solo el destinatario puede responder este intercambio")

        # Datos necesarios para validar reglas en dominio (roles y fechas)
        requester = await self.user_repository.find_by_id(swap.requester_user_id)
        target = await self.user_repository.find_by_id(swap.target_user_id)
        if not requester or not target:
            raise NotFoundException("Usuario", swap.target_user_id if not target else swap.requester_user_id)

        req_shift = await self.work_schedule_repository.find_shift_by_id(swap.requester_shift_id)
        tgt_shift = await self.work_schedule_repository.find_shift_by_id(swap.target_shift_id)
        if not req_shift or not tgt_shift:
            raise NotFoundException("Turno", swap.requester_shift_id if not req_shift else swap.target_shift_id)

        if cmd.accept:
            if not req_shift.valid_from or not tgt_shift.valid_from:
                raise DomainException("No se pudo determinar la fecha de los turnos")
            requester_shift_start = datetime.combine(req_shift.valid_from, req_shift.start_time, tzinfo=timezone.utc)
            target_shift_start = datetime.combine(tgt_shift.valid_from, tgt_shift.start_time, tzinfo=timezone.utc)

            # Llama a la lógica de dominio (valida 48h, etc.)
            swap.accept(
                actor_user_id=cmd.responder_id,
                requester_role=requester.role.value if hasattr(requester.role, "value") else requester.role,
                target_role=target.role.value if hasattr(target.role, "value") else target.role,
                requester_shift_start_utc=requester_shift_start,
                target_shift_start_utc=target_shift_start,
                now_utc=datetime.now(timezone.utc),
            )
            swap.status = SwapStatus.ACCEPTED
            msg = "Intercambio aceptado"
        else:
            swap.reject(actor_user_id=cmd.responder_id)
            swap.status = SwapStatus.REJECTED
            msg = "Intercambio rechazado"

        if cmd.note:
            swap.note = (swap.note or "") + f"\nRespuesta: {cmd.note}"

        saved = await self.swap_repository.save(swap)
        return {"success": True, "message": msg, "swap": saved}
