"""Servicio de autenticación JWT"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from app.users.application.ports.auth_service import AuthService
from app.users.domain.user import User


class JWTAuthService(AuthService):
    """Implementación del servicio de autenticación con JWT"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    async def generate_access_token(self, user: User) -> str:
        """Genera un token JWT de acceso"""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expire_minutes
        )

        payload = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value,
            "type": "access",
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    async def generate_refresh_token(self, user: User) -> str:
        """Genera un token JWT de refresh"""
        expire = datetime.now(timezone.utc) + timedelta(
            days=self.refresh_token_expire_days
        )

        payload = {
            "sub": user.id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    async def verify_token(self, token: str) -> Optional[dict]:
        """Verifica y decodifica un token JWT"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            # Token expirado
            return None
        except jwt.InvalidTokenError:
            # Token inválido
            return None