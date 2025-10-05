from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timezone, timedelta
from app.building_blocks.exceptions import DomainException

@dataclass
class ActivationToken:
    """
    Entidad de dominio para tokens de activación.
    Un token es de un solo uso y tiene fecha de expiración.
    """
    id: Optional[str] = None
    token: str = ""
    user_id: str = ""
    employee_id: str = ""  # Para validación adicional

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=48))
    used_at: Optional[datetime] = None
    is_used: bool = False

    def is_valid(self) -> bool:
        """
        Verifica si el token es válido:
        - No ha sido usado
        - No ha expirado
        """
        if self.is_used:
            return False

        return datetime.now(timezone.utc) <= self.expires_at

    def mark_as_used(self) -> None:
        """Marca el token como usado"""
        if self.is_used:
            raise DomainException("El token ya ha sido usado")

        if not self.is_valid():
            raise DomainException("El token ha expirado")

        self.is_used = True
        self.used_at = datetime.now(timezone.utc)

    def is_expired(self) -> bool:
        """Verifica si el token ha expirado"""
        return datetime.now(timezone.utc) > self.expires_at

    @staticmethod
    def generate_secure_token() -> str:
        """Genera un token seguro de 32 bytes (64 caracteres hex)"""
        import secrets
        return secrets.token_urlsafe(32)