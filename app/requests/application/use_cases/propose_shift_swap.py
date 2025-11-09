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
        user_repository: UserRepository,
    ):
        self.swap_repository = swap_repository
        self.work_schedule_repository = work_schedule_repository
        self.user_repository = user_repository

    async def execute(self, cmd: ProposeShiftSwapCommand) -> dict:
        requester = await self.user_repository.find_by_id(cmd.requester_id)
        target = await self.user_repository.find_by_id(cmd.target_user_id)
        if not requester or not target:
            raise NotFoundException("Usuario", cmd.target_user_id if not target else cmd.requester_id)

        if requester.role != target.role:
            raise DomainException("Ambos usuarios deben tener el mismo rol para intercambiar turnos")

        req_shift = await self.work_schedule_repository.find_shift_by_id(cmd.requester_shift_id)
        tgt_shift = await self.work_schedule_repository.find_shift_by_id(cmd.target_shift_id)
        if not req_shift or not tgt_shift:
            raise NotFoundException("Turno", cmd.requester_shift_id if not req_shift else cmd.target_shift_id)

        if req_shift.user_id != cmd.requester_id or tgt_shift.user_id != cmd.target_user_id:
            raise DomainException("Cada turno debe pertenecer al usuario correspondiente")

        # Regla 48h: usamos la fecha de inicio de vigencia del turno + hora de inicio
        if not req_shift.valid_from:
            raise DomainException("El turno del solicitante no tiene fecha de vigencia definida")

        window_limit = datetime.now(timezone.utc) + timedelta(hours=48)
        requester_shift_start = datetime.combine(req_shift.valid_from, req_shift.start_time, tzinfo=timezone.utc)
        if requester_shift_start < window_limit:
            raise DomainException("Los intercambios deben solicitarse con al menos 48 horas de anticipación")

        swap = ShiftSwapRequest(
            requester_id=cmd.requester_id,
            target_user_id=cmd.target_user_id,
            requester_shift_id=cmd.requester_shift_id,
            target_shift_id=cmd.target_shift_id,
            status=SwapStatus.PENDING,
            note=cmd.note or "",
        )

        saved = await self.swap_repository.save(swap)
        return {
            "success": True,
            "message": "Intercambio propuesto",
            "swap": saved,  # <- para que GraphQL pueda mapearlo directo
        }
