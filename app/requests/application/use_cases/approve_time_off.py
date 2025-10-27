"""Caso de uso: Aprobar solicitud (admin)"""
from dataclasses import dataclass
from app.requests.application.ports.time_off_request_repository import TimeOffRequestRepository
from app.requests.application.ports.vacation_balance_repository import VacationBalanceRepository
from app.requests.domain.request_status import RequestStatus,RequestType
from app.building_blocks.exceptions import DomainException, NotFoundException

@dataclass
class ApproveTimeOffCommand:
    request_id: str
    admin_id: str  # se usa para auditoría, la verificación de rol se hace en la capa GraphQL

class ApproveTimeOffUseCase:
    def __init__(self, request_repository: TimeOffRequestRepository, balance_repository: VacationBalanceRepository):
        self.request_repository = request_repository
        self.balance_repository = balance_repository

    async def execute(self, cmd: ApproveTimeOffCommand) -> dict:
        req = await self.request_repository.find_by_id(cmd.request_id)
        if not req:
            raise NotFoundException("Solicitud", cmd.request_id)

        if req.status != RequestStatus.PENDING:
            raise DomainException("Solo puedes aprobar solicitudes en estado pending")

        # Si es VACATION y NO se consumió al crear, consumir ahora
        if req.type == RequestType.VACATION and not req.audit.get("consumed_on_request", False):
            balance = await self.balance_repository.get_for_user_year(req.user_id, req.start_date.year)
            if not balance or not balance.can_consume(req.days_requested):
                raise DomainException("Saldo insuficiente al aprobar")
            balance.consume(req.days_requested)
            await self.balance_repository.save(balance)
            req.audit["consumed_on_approve"] = req.days_requested

        req.status = RequestStatus.APPROVED
        req.audit["approved_by"] = cmd.admin_id
        saved = await self.request_repository.save(req)
        return {"success": True, "status": saved.status.value, "message": "Solicitud aprobada"}
