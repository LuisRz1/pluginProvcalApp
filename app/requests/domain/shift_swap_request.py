from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.building_blocks.exceptions import DomainException
from app.requests.domain.request_status import SwapStatus


@dataclass
class ShiftSwapRequest:
    """
    Solicitud de intercambio de turnos.
    Reglas:
    - propose(): crea en estado pending
    - accept(): solo el target_user; rol-igual; fecha/turno de ambos ≥ 48h desde ahora
    - reject(): solo el target_user y si está pending
    - cancel(): solo el requester_user y si está pending

    NOTA: Para mantener el dominio puro, las verificaciones de rol y
    datetimes reales de turnos se inyectan como argumentos (la app los
    obtiene desde UserRepository y WorkScheduleRepository).
    """
    id: Optional[str] = None

    requester_user_id: str = ""
    requester_shift_id: str = ""

    target_user_id: str = ""
    target_shift_id: str = ""

    status: SwapStatus = SwapStatus.PENDING
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    responded_at: Optional[datetime] = None

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # ---- Fábrica/acción ----
    @staticmethod
    def propose(requester_user_id: str, requester_shift_id: str,
                target_user_id: str, target_shift_id: str) -> "ShiftSwapRequest":
        """Crea una solicitud en estado pending."""
        return ShiftSwapRequest(
            requester_user_id=requester_user_id,
            requester_shift_id=requester_shift_id,
            target_user_id=target_user_id,
            target_shift_id=target_shift_id,
            status=SwapStatus.PENDING
        )

    # ---- Acciones con reglas ----
    def accept(
        self,
        actor_user_id: str,
        requester_role: str,
        target_role: str,
        requester_shift_start_utc: datetime,
        target_shift_start_utc: datetime,
        now_utc: Optional[datetime] = None
    ) -> None:
        """
        Acepta el intercambio.
        Reglas:
        - Solo el target_user puede aceptar
        - Roles iguales (misma familia/rol operativo)
        - Ambos turnos con al menos 48h de anticipación respecto a 'ahora'
        """
        if self.status != SwapStatus.PENDING:
            raise DomainException("Solo se pueden aceptar solicitudes en estado pendiente")

        if actor_user_id != self.target_user_id:
            raise DomainException("Solo el empleado destinatario puede aceptar el intercambio")

        if requester_role != target_role:
            raise DomainException("Ambos empleados deben tener el mismo rol")

        now = now_utc or datetime.now(timezone.utc)
        horizon = timedelta(hours=48)
        if (requester_shift_start_utc - now) < horizon or (target_shift_start_utc - now) < horizon:
            raise DomainException("El intercambio debe confirmarse con al menos 48 horas de anticipación")

        self.status = SwapStatus.ACCEPTED
        self.responded_at = now
        self.updated_at = now

    def reject(self, actor_user_id: str) -> None:
        """Rechaza la solicitud (solo target_user; pendiente)."""
        if self.status != SwapStatus.PENDING:
            raise DomainException("Solo se pueden rechazar solicitudes en estado pendiente")
        if actor_user_id != self.target_user_id:
            raise DomainException("Solo el empleado destinatario puede rechazar")
        now = datetime.now(timezone.utc)
        self.status = SwapStatus.REJECTED
        self.responded_at = now
        self.updated_at = now

    def cancel(self, actor_user_id: str) -> None:
        """Cancela la solicitud (solo requester_user; pendiente)."""
        if self.status != SwapStatus.PENDING:
            raise DomainException("Solo se pueden cancelar solicitudes en estado pendiente")
        if actor_user_id != self.requester_user_id:
            raise DomainException("Solo el solicitante puede cancelar")
        self.status = SwapStatus.CANCELLED
        self.updated_at = datetime.now(timezone.utc)
