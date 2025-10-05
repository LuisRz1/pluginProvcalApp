from abc import ABC, abstractmethod
from typing import Optional

class EmailService(ABC):
    """Puerto para el servicio de email"""

    @abstractmethod
    async def send_activation_email(
        self,
        to_email: str,
        user_name: str,
        activation_link: str,
        expires_in_hours: int = 48
    ) -> bool:
        """
        Envía un email de activación de cuenta.

        Args:
            to_email: Email del destinatario
            user_name: Nombre del usuario
            activation_link: Link de activación completo
            expires_in_hours: Horas hasta la expiración

        Returns:
            True si el email fue enviado exitosamente
        """
        pass

    @abstractmethod
    async def send_account_activated_email(
        self,
        to_email: str,
        user_name: str
    ) -> bool:
        """Envía confirmación de cuenta activada"""
        pass
    