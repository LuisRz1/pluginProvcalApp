from abc import ABC, abstractmethod
from typing import Optional
from app.users.domain.user import User

class AuthService(ABC):
    """Puerto para el servicio de autenticación"""

    @abstractmethod
    async def generate_access_token(self, user: User) -> str:
        """Genera un token JWT de acceso"""
        pass

    @abstractmethod
    async def generate_refresh_token(self, user: User) -> str:
        """Genera un token JWT de refresh"""
        pass

    @abstractmethod
    async def verify_token(self, token: str) -> Optional[dict]:
        """Verifica y decodifica un token JWT"""
        pass