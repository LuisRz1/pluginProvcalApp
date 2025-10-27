"""Caso de uso: Proponer intercambio de turno"""
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from app.requests.domain.shift_swap_request import ShiftSwapRequest
from app.requests.domain.request_status import SwapStatus
from app.requests.application.ports.shift_swap_repository import ShiftSwapRepository
from app.requests.application.ports.work_schedule_repository import WorkScheduleRepository
from app.users.application.ports.user_repository import UserRepository
from app.building_blocks.exceptions import DomainException, NotFoundException

@dataclass
class ProposeShiftSwapCommand:
    requester_id: str
    target_user_id: str
    requester_shift_id: str
    target_shift_id: str
    note: str | None = None

class ProposeShiftSwapUseCase:
    def __init__(
        self,
        swap_repository: ShiftSwapRepository,
        work_schedule_repository: WorkScheduleRepository,
        user_repository: UserRepository
    ):
        self.swap_repository = swap_repository
        self.work_schedule_repository = work_schedule_repository
        self.user_repository = user_repository

    async def execute(self, cmd: ProposeShiftSwapCommand) -> dict:
        # 1) Validar que ambos usuarios existan y roles sean iguales
        requester = await self.user_repository.find_by_id(cmd.requester_id)
        target = await self.user_repository.find_by_id(cmd.target_user_id)
        if not requester or not target:
            raise NotFoundException("Usuario", cmd.target_user_id if not target else cmd.requester_id)

        if requester.role != target.role:
            raise DomainException("Ambos usuarios deben tener el mismo rol para intercambiar turnos")

        # 2) Validar que los turnos existan y pertenezcan al usuario indicado
        req_shift = await self.work_schedule_repository.find_shift_by_id(cmd.requester_shift_id)
        tgt_shift = await self.work_schedule_repository.find_shift_by_id(cmd.target_shift_id)
        if not req_shift or not tgt_shift:
            raise NotFoundException("Turno", cmd.requester_shift_id if not req_shift else cmd.target_shift_id)

        if req_shift.user_id != cmd.requester_id or tgt_shift.user_id != cmd.target_user_id:
            raise DomainException("Cada turno debe pertenecer al usuario correspondiente")

        # 3) Validar ventana de 48h (usamos fecha del turno del solicitante)
        today_plus_2 = datetime.now(timezone.utc).date() + timedelta(days=2)
        # Se asume que la vigencia/fecha del turno se deriva de valid_from/valid_to o consulta diaria
        shift_date = req_shift.valid_from or today_plus_2  # fallback, ideal: fecha exacta del turno
        if shift_date < today_plus_2:
            raise DomainException("Los intercambios deben solicitarse con al menos 48 horas de anticipación")

        swap = ShiftSwapRequest(
            requester_id=cmd.requester_id,
            target_user_id=cmd.target_user_id,
            requester_shift_id=cmd.requester_shift_id,
            target_shift_id=cmd.target_shift_id,
            status=SwapStatus.PENDING,
            note=cmd.note or ""
        )

        saved = await self.swap_repository.save(swap)
        return {"success": True, "swap_id": saved.id, "status": saved.status.value}
