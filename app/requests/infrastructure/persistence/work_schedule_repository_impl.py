"""Repositorio de solo lectura para horarios de trabajo"""
from typing import Optional
import uuid

from sqlalchemy import Column, String, Date, Time, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID

from app.requests.application.ports.work_schedule_repository import WorkScheduleRepository

Base = declarative_base()

class WorkScheduleModel(Base):
    __tablename__ = "work_schedules"  # o 'horarios_trabajo' si ya existe así

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Ventana de validez para el turno (si llevas esquema diario, puedes usar solo 'date')
    valid_from = Column(Date, nullable=False, index=True)
    valid_to = Column(Date, nullable=False, index=True)

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # campos extra opcionales (ej. location_id, role, etc.)
    role = Column(String(50), nullable=True)

class ShiftDTO:
    """DTO liviano para la capa de aplicación"""
    def __init__(self, id: str, user_id: str, valid_from, valid_to, start_time, end_time, role: str | None):
        self.id = id
        self.user_id = user_id
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.start_time = start_time
        self.end_time = end_time
        self.role = role

class PostgreSQLWorkScheduleRepository(WorkScheduleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_shift_by_id(self, shift_id: str) -> Optional[ShiftDTO]:
        stmt = select(WorkScheduleModel).where(WorkScheduleModel.id == shift_id)
        result = await self.session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._to_dto(m) if m else None

    async def find_user_shift_on(self, on_date, user_id: str) -> Optional[ShiftDTO]:
        stmt = select(WorkScheduleModel).where(
            WorkScheduleModel.user_id == user_id,
            WorkScheduleModel.valid_from <= on_date,
            WorkScheduleModel.valid_to >= on_date,
        )
        result = await self.session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._to_dto(m) if m else None

    @staticmethod
    def _to_dto(m: WorkScheduleModel) -> ShiftDTO:
        return ShiftDTO(
            id=str(m.id),
            user_id=str(m.user_id),
            valid_from=m.valid_from,
            valid_to=m.valid_to,
            start_time=m.start_time,
            end_time=m.end_time,
            role=m.role,
        )
