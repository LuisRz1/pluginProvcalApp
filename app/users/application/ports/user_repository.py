"""
Puerto (interfaz) para el repositorio de usuarios.
Define el contrato que debe cumplir cualquier implementación.
"""
from abc import ABC, abstractmethod
from typing import Optional
from app.users.domain.user import User


class UserRepository(ABC):
    """Puerto para el repositorio de usuarios"""

    @abstractmethod
    async def save(self, user: User) -> User:
        """
        Guarda o actualiza un usuario.

        Args:
            user: Usuario a guardar

        Returns:
            Usuario guardado con ID asignado
        """


    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """
        Busca un usuario por ID.

        Args:
            user_id: ID del usuario

        Returns:
            Usuario encontrado o None
        """
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """
        Busca un usuario por email.

        Args:
            email: Email del usuario

        Returns:
            Usuario encontrado o None
        """
        pass

    @abstractmethod
    async def find_by_employee_id(self, employee_id: str) -> Optional[User]:
        """
        Busca un usuario por employee_id.

        Args:
            employee_id: ID de empleado

        Returns:
            Usuario encontrado o None
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """
        Verifica si existe un usuario con ese email.

        Args:
            email: Email a verificar

        Returns:
            True si existe, False si no
        """
        pass

    @abstractmethod
    async def exists_by_employee_id(self, employee_id: str) -> bool:
        """
        Verifica si existe un usuario con ese employee_id.

        Args:
            employee_id: Employee ID a verificar

        Returns:
            True si existe, False si no
        """
        pass