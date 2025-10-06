"""Puerto para repositorio de asistencia"""
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date
from app.attendance.domain.attendance import Attendance

class AttendanceRepository(ABC):

    @abstractmethod
    async def save(self, attendance: Attendance) -> Attendance:
        """Guarda o actualiza una asistencia"""


    @abstractmethod
    async def find_by_id(self, attendance_id: str) -> Optional[Attendance]:
        """Busca una asistencia por ID"""


    @abstractmethod
    async def find_by_user_and_date(self, user_id: str, date: date) -> Optional[Attendance]:
        """Busca la asistencia de un usuario para una fecha específica"""


    @abstractmethod
    async def find_by_user(self, user_id: str, limit: int = 30) -> List[Attendance]:
        """Obtiene las últimas asistencias de un usuario"""


    @abstractmethod
    async def has_pending_regularization(self, user_id: str) -> bool:
        """Verifica si el usuario tiene asistencias pendientes de regularizar"""

