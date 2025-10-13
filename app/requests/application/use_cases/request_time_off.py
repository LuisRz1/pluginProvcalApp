"""Caso de uso: Solicitar tiempo libre (vacaciones/permiso)"""
from dataclasses import dataclass
from datetime import date, timedelta, timezone, datetime

from app.requests.domain.time_off_request import TimeOffRequest
from app.requests.domain.request_status import RequestStatus,RequestType
from app.requests.application.ports.time_off_request_repository import TimeOffRequestRepository
from app.requests.application.ports.vacation_balance_repository import VacationBalanceRepository
from app.building_blocks.exceptions import DomainException

@dataclass
class RequestTimeOffCommand:
    user_id: str
    type: RequestType
    start_date: date
    end_date: date
    reason: str
    consume_on_request: bool = True  # ver nota en el mensaje

@dataclass
class RequestTimeOffResponse:
    request_id: str
    status: str
    days_requested: int
    message: str

class RequestTimeOffUseCase:
    def __init__(
        self,
        request_repository: TimeOffRequestRepository,
        balance_repository: VacationBalanceRepository
    ):
        self.request_repository = request_repository
        self.balance_repository = balance_repository

    async def execute(self, cmd: RequestTimeOffCommand) -> RequestTimeOffResponse:
        # 1) Regla ventana mínima 48h (start >= hoy+2) – se valida en la entidad también
        now_utc = datetime.now(timezone.utc)
        if cmd.start_date < (now_utc.date() + timedelta(days=2)):
            raise DomainException("La solicitud debe hacerse con al menos 48 horas de anticipación")

        # 2) Calcular días completos (incluye fines/feriados)
        if cmd.end_date < cmd.start_date:
            raise DomainException("El rango de fechas es inválido")
        days_requested = (cmd.end_date - cmd.start_date).days + 1

        # 3) Si es VACATION, verificar saldo y (opcional) consumir
        audit = {
            "consumed_on_request": False,
            "reason": cmd.reason,
            "created_at": now_utc.isoformat()
        }

        if cmd.type == RequestType.VACATION:
            balance = await self.balance_repository.get_for_user_year(cmd.user_id, cmd.start_date.year)
            if not balance:
                raise DomainException("No tienes saldo de vacaciones configurado para este año")

            if not balance.can_consume(days_requested):
                raise DomainException("No tienes días suficientes en tu saldo de vacaciones")

            if cmd.consume_on_request:
                balance.consume(days_requested)
                await self.balance_repository.save(balance)
                audit["consumed_on_request"] = True
                audit["consumed_days"] = days_requested

        # 4) Crear solicitud en estado pending
        req = TimeOffRequest(
            user_id=cmd.user_id,
            type=cmd.type,
            start_date=cmd.start_date,
            end_date=cmd.end_date,
            days_requested=days_requested,
            status=RequestStatus.PENDING,
            reason=cmd.reason,
            audit=audit
        )
        # valida reglas embebidas (ventana + cálculo días) dentro del modelo
        req.validate_window(now_utc=now_utc)

        saved = await self.request_repository.save(req)

        return RequestTimeOffResponse(
            request_id=saved.id,
            status=saved.status.value,
            days_requested=saved.days_requested,
            message="Solicitud creada correctamente"
        )
