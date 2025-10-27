from dataclasses import dataclass, field
from datetime import datetime, date, timezone, timedelta
from typing import Optional, Dict, Any
from zoneinfo import ZoneInfo

from app.building_blocks.exceptions import DomainException
from app.requests.domain.request_status import RequestType, RequestStatus

@dataclass
class TimeOffRequest:
    """
    Solicitud de días (vacaciones o permiso).
    Reglas:
    - DÍAS COMPLETOS (incluye fines de semana y feriados)
    - Ventana mínima: start_date >= hoy(Lima) + 2 días
    - days_requested == (end_date - start_date + 1)
    - cancel() solo si status == pending
    """
    id: Optional[str] = None
    user_id: str = ""
    type: RequestType = RequestType.VACATION

    start_date: date = field(default_factory=lambda: datetime.now(ZoneInfo("America/Lima")).date())
    end_date: date = field(default_factory=lambda: datetime.now(ZoneInfo("America/Lima")).date())
    days_requested: int = 1

    status: RequestStatus = RequestStatus.PENDING
    reason: Optional[str] = None

    audit: Dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        self._validate_dates_consistency()
        self._validate_window(datetime.now(timezone.utc), tz="America/Lima")

    # ----- Reglas embebidas -----

    def _validate_dates_consistency(self) -> None:
        """end_date >= start_date y days_requested == diff + 1."""
        if self.end_date < self.start_date:
            raise DomainException("La fecha fin no puede ser menor a la fecha inicio")

        diff_days = (self.end_date - self.start_date).days + 1
        if self.days_requested != diff_days:
            raise DomainException("days_requested debe ser igual a los días calendario del rango")

        if self.days_requested < 1:
            raise DomainException("Debes solicitar al menos 1 día")

    def _validate_window(self, now_utc: datetime, tz: str = "America/Lima") -> None:
        """
        start_date >= hoy(tz) + 2 días.
        """
        local_today = now_utc.astimezone(ZoneInfo(tz)).date()
        min_start = local_today + timedelta(days=2)
        if self.start_date < min_start:
            raise DomainException("La solicitud debe hacerse con al menos 48 horas de anticipación")

    # API de dominio
    def cancel(self) -> None:
        """Cancela la solicitud (solo si está pendiente)."""
        if self.status != RequestStatus.PENDING:
            raise DomainException("Solo puedes cancelar solicitudes en estado pendiente")
        self.status = RequestStatus.CANCELLED
        self.updated_at = datetime.now(timezone.utc)
