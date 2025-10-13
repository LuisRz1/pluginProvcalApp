"""Caso de uso: Rechazar solicitud (admin)"""
from dataclasses import dataclass
from app.requests.application.ports.time_off_request_repository import TimeOffRequestRepository
from app.requests.application.ports.vacation_balance_repository import VacationBalanceRepository
from app.requests.domain.request_status import RequestStatus, RequestType
from app.building_blocks.exceptions import DomainException, NotFoundException

@dataclass
class RejectTimeOffCommand:
    request_id: str
    admin_id: str
    reason: str

class RejectTimeOffUseCase:
    def __init__(self, request_repository: TimeOffRequestRepository, balance_repository: VacationBalanceRepository):
        self.request_repository = request_repository
        self.balance_repository = balance_repository

    async def execute(self, cmd: RejectTimeOffCommand) -> dict:
        req = await self.request_repository.find_by_id(cmd.request_id)
        if not req:
            raise NotFoundException("Solicitud", cmd.request_id)

        if req.status != RequestStatus.PENDING:
            raise DomainException("Solo puedes rechazar solicitudes en estado pending")

        # Si consumimos al crear y es VACATION => refund
        consumed = bool(req.audit.get("consumed_on_request"))
        consumed_days = int(req.audit.get("consumed_days", 0))
        if consumed and req.type == RequestType.VACATION and consumed_days > 0:
            balance = await self.balance_repository.get_for_user_year(req.user_id, req.start_date.year)
            if balance:
                balance.refund(consumed_days)
                await self.balance_repository.save(balance)
            req.audit["refund_on_reject"] = consumed_days

        req.status = RequestStatus.REJECTED
        req.audit["rejected_by"] = cmd.admin_id
        req.audit["reject_reason"] = cmd.reason

        saved = await self.request_repository.save(req)
        return {"success": True, "status": saved.status.value, "message": "Solicitud rechazada"}
