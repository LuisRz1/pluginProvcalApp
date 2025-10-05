from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
import re
import bcrypt
from app.building_blocks.exceptions import DomainException
from app.users.domain.user_role import UserRole

class UserStatus(Enum):
    PENDING_ACTIVATION = "pending_activation"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

@dataclass
class User:
    """
    Entidad de dominio Usuario.
    Representa a un empleado en el sistema de catering.
    """
    id: Optional[str] = None
    employee_id: str = ""  # ID proporcionado por RRHH
    email: str = ""     # Email corporativo
    personal_email: Optional[str] = None
    password_hash: Optional[str] = None
    role: UserRole = UserRole.EMPLOYEE
    status: UserStatus = UserStatus.PENDING_ACTIVATION

    # Datos proporcionados por RRHH
    full_name: str = ""
    dni: str = ""
    phone: Optional[str] = None
    address: Optional[str] = None

    # Flags de consentimiento
    data_processing_consent: bool = False
    data_processing_consent_date: Optional[datetime] = None

    # Auditoría
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None  # ID del admin que creó la cuenta
    activated_at: Optional[datetime] = None

    # Historial de contraseñas (hashes)
    previous_passwords: list[str] = field(default_factory=list)

    def __post_init__(self):
        self._validate()

    def _validate(self):
        """Validaciones básicas del dominio"""
        if self.email and not self._is_valid_email(self.email):
            raise DomainException("Email inválido")

        if self.personal_email and not self._is_valid_email(self.personal_email):
            raise DomainException("Email personal inválido")

        if not self.employee_id:
            raise DomainException("Employee ID es requerido")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def set_password(self, password: str) -> None:
        """
        Establece la contraseña del usuario con validaciones de seguridad.
        """
        # Validar política de contraseñas
        self._validate_password_policy(password)

        # Verificar que no sea una contraseña previa
        if self._is_previous_password(password):
            raise DomainException(
                "No puedes usar una contraseña que hayas usado anteriormente"
            )

        # Guardar hash de contraseña anterior si existe
        if self.password_hash:
            self.previous_passwords.append(self.password_hash)
            # Mantener solo las últimas 5 contraseñas
            if len(self.previous_passwords) > 5:
                self.previous_passwords = self.previous_passwords[-5:]

        # Hashear y guardar nueva contraseña
        self.password_hash = self._hash_password(password)
        self.updated_at = datetime.now(timezone.utc)

    def _validate_password_policy(self, password: str) -> None:
        """
        Política de contraseñas:
        - Mínimo 8 caracteres
        - Al menos una mayúscula
        - Al menos una minúscula
        - Al menos un número
        - Al menos un carácter especial
        """
        if len(password) < 8:
            raise DomainException("La contraseña debe tener al menos 8 caracteres")

        if not re.search(r'[A-Z]', password):
            raise DomainException("La contraseña debe contener al menos una mayúscula")

        if not re.search(r'[a-z]', password):
            raise DomainException("La contraseña debe contener al menos una minúscula")

        if not re.search(r'\d', password):
            raise DomainException("La contraseña debe contener al menos un número")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise DomainException(
                "La contraseña debe contener al menos un carácter especial"
            )

    def _is_previous_password(self, password: str) -> bool:
        """Verifica si la contraseña ya fue usada anteriormente"""
        for prev_hash in self.previous_passwords:
            if bcrypt.checkpw(password.encode('utf-8'), prev_hash.encode('utf-8')):
                return True

        # Verificar también contra la contraseña actual si existe
        if self.password_hash:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                self.password_hash.encode('utf-8')
            )

        return False

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hashea la contraseña usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """Verifica si la contraseña proporcionada es correcta"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def activate(
        self,
        password: str,
        personal_email: str,
        data_consent: bool
    ) -> None:
        """
        Activa la cuenta del usuario.
        Solo puede activarse si está en estado PENDING_ACTIVATION.
        """
        if self.status != UserStatus.PENDING_ACTIVATION:
            raise DomainException("La cuenta no está pendiente de activación")

        if not data_consent:
            raise DomainException(
                "Debes aceptar el tratamiento de datos para activar tu cuenta"
            )

        # Establecer contraseña
        self.set_password(password)

        # Actualizar email personal
        if not self._is_valid_email(personal_email):
            raise DomainException("Email personal inválido")
        self.personal_email = personal_email

        # Marcar consentimiento
        self.data_processing_consent = True
        self.data_processing_consent_date = datetime.now(timezone.utc)

        # Cambiar estado
        self.status = UserStatus.ACTIVE
        self.activated_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def can_activate(self) -> bool:
        """Verifica si el usuario puede ser activado"""
        return self.status == UserStatus.PENDING_ACTIVATION

    def deactivate(self) -> None:
        """Desactiva la cuenta del usuario"""
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.now(timezone.utc)

    def suspend(self) -> None:
        """Suspende la cuenta del usuario"""
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.now(timezone.utc)