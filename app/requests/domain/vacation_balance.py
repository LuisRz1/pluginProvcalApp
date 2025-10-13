from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from app.building_blocks.exceptions import DomainException

@dataclass
class VacationBalance:
    """
    Saldo de vacaciones por usuario y año calendario.
    """
    user_id: str
    year: int
    total_days: int = 30
    used_days: int = 0

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def available_days(self) -> int:
        """Días disponibles = total - usados."""
        return max(0, self.total_days - self.used_days)

    def can_consume(self, n: int) -> bool:
        """¿Se pueden consumir n días?"""
        return n >= 1 and self.available_days() >= n

    def consume(self, n: int) -> None:
        """Consume n días (valida disponibilidad)."""
        if n < 1:
            raise DomainException("Debes solicitar al menos 1 día")
        if not self.can_consume(n):
            raise DomainException("No hay días de vacaciones suficientes")
        self.used_days += n
        self.updated_at = datetime.now(timezone.utc)

    def refund(self, n: int) -> None:
        """Devuelve n días (por cancelación/rechazo)."""
        if n < 1:
            raise DomainException("La devolución debe ser de al menos 1 día")
        if self.used_days - n < 0:
            raise DomainException("No puedes devolver más días de los usados")
        self.used_days -= n
        self.updated_at = datetime.now(timezone.utc)
