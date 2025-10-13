"""Puerto para repositorio de horarios"""
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date
from app.attendance.domain.work_schedule import WorkSchedule

class WorkScheduleRepository(ABC):

    @abstractmethod
    async def save(self, schedule: WorkSchedule) -> WorkSchedule:
        """Guarda o actualiza un horario"""


    @abstractmethod
    async def find_by_id(self, schedule_id: str) -> Optional[WorkSchedule]:
        """Busca un horario por ID"""


    @abstractmethod
    async def find_active_by_user(self, user_id: str) -> Optional[WorkSchedule]:
        """Obtiene el horario activo de un usuario"""


    @abstractmethod
    async def find_by_user_and_date(
        self,
        user_id: str,
        check_date: date
    ) -> Optional[WorkSchedule]:
        """Obtiene el horario válido para un usuario en una fecha específica"""


    @abstractmethod
    async def find_history_by_user(self, user_id: str) -> List[WorkSchedule]:
        """Obtiene el historial de horarios de un usuario"""
