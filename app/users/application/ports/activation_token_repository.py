"""
Puerto (interfaz) para el repositorio de tokens de activación.
Define el contrato que debe cumplir cualquier implementación.
"""
from abc import ABC, abstractmethod
from typing import Optional
from app.users.domain.activation_token import ActivationToken


class ActivationTokenRepository(ABC):
    """Puerto para el repositorio de tokens de activación"""

    @abstractmethod
    async def save(self, token: ActivationToken) -> ActivationToken:
        """
        Guarda un token de activación.

        Args:
            token: Token a guardar

        Returns:
            Token guardado con ID asignado
        """

    @abstractmethod
    async def find_by_token(self, token: str) -> Optional[ActivationToken]:
        """
        Busca un token por su valor.

        Args:
            token: Valor del token

        Returns:
            Token encontrado o None
        """

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> Optional[ActivationToken]:
        """
        Busca tokens de un usuario específico.
        Retorna el más reciente.

        Args:
            user_id: ID del usuario

        Returns:
            Token más reciente o None
        """

    @abstractmethod
    async def invalidate_user_tokens(self, user_id: str) -> None:
        """
        Invalida todos los tokens activos de un usuario.

        Args:
            user_id: ID del usuario
        """
