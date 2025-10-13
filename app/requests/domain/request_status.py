"""Estados y tipos de solicitudes de tiempo libre e intercambio de turnos"""
from enum import Enum

class RequestStatus(Enum):
    """Estado de una solicitud de días."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class RequestType(Enum):
    """Tipo de solicitud de días (por días completos)."""
    VACATION = "vacation"
    PERMISSION = "permission"

class SwapStatus(Enum):
    """Estado de una solicitud de intercambio de turno."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
