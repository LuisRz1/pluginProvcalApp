"""Repositorio de solo lectura para horarios de trabajo"""
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import Column, String, Time, Date, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import select

from app.requests.application.ports.work_schedule_repository import (
    WorkScheduleRepository,
    WorkShiftSummary,
)

Base = declarative_base()

class WorkScheduleModel(Base):
    """
    Modelo SQLAlchemy que representa la tabla work_schedules
    creada en la migración 003_create_work_schedules_table.py

    Esta tabla define el horario/turno asignado a un usuario,
    incluyendo rango de vigencia (effective_from / effective_until),
    tipo de turno (shift_type), y horas de inicio/fin.
    """

    __tablename__ = "work_schedules"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)

    # Ej: "morning", "afternoon", "night", "custom"
    shift_type = Column(String(50), nullable=False, index=True)

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # Días de la semana en que aplica el turno (ej [0,1,2,3,4])
    # En Alembic 003 esto suele ser ARRAY(Integer) o JSON.
    # Lo incluimos para reflejar la tabla aunque en los swaps no lo usamos directamente.
    working_days = Column(ARRAY(Integer), nullable=False)

    late_tolerance_minutes = Column(Integer, nullable=False, server_default=sa.text("5"))
    break_duration_minutes = Column(Integer, nullable=False, server_default=sa.text("30"))

    is_active = Column(Boolean, nullable=False, server_default=sa.text("true"), index=True)

    # Vigencia del turno
    effective_from = Column(Date, nullable=False, index=True)
    effective_until = Column(Date, nullable=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    notes = Column(String(500), nullable=True)


class PostgreSQLWorkScheduleRepository(WorkScheduleRepository):
    """
    Implementación Postgres del WorkScheduleRepository para el módulo requests.

    Esta capa se usa principalmente por los casos de uso de intercambio de turnos
    (ProposeShiftSwapUseCase / RespondShiftSwapUseCase) para:
    - Verificar que cierto turno le pertenece realmente al usuario.
    - Obtener la info básica del turno (shift_type, horas).
    - Consultar qué turno aplica en una fecha dada.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # ---------------------------------
    # Helpers internos
    # ---------------------------------

    def _to_summary(self, m: WorkScheduleModel) -> WorkShiftSummary:
        """
        Convierte un modelo ORM (WorkScheduleModel) en el DTO
        WorkShiftSummary definido en la capa de puertos.
        """
        return WorkShiftSummary(
            id=str(m.id),
            user_id=str(m.user_id),
            shift_type=m.shift_type,
            start_time=m.start_time,
            end_time=m.end_time,
            effective_from=m.effective_from,
            effective_until=m.effective_until,
        )

    # ---------------------------------
    # Métodos del puerto
    # ---------------------------------

    async def find_shift_by_id(self, shift_id: str) -> Optional[WorkShiftSummary]:
        """
        Trae un turno específico por ID.
        Útil para validar que:
        - el turno existe
        - y luego el caso de uso valida que pertenece al usuario correcto.
        """
        stmt = (
            select(WorkScheduleModel)
            .where(WorkScheduleModel.id == uuid.UUID(shift_id))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        model: Optional[WorkScheduleModel] = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_summary(model)

    async def find_user_shift_on(
        self,
        check_date: date,
        user_id: str,
    ) -> Optional[WorkShiftSummary]:
        """
        Devuelve el turno vigente de un usuario para una fecha dada.

        Regla:
        - Debe ser un horario activo (is_active = true).
        - Debe estar dentro del rango de vigencia:
              effective_from <= check_date <= effective_until
          o bien si effective_until es NULL, asumimos que sigue vigente.
        - NOTA: aquí no filtramos por working_days. Eso le da flexibilidad al
          caso de uso; si más adelante quieres forzar que el día de la semana
          coincida con working_days, puedes agregarlo acá.
        """

        stmt = (
            select(WorkScheduleModel)
            .where(
                WorkScheduleModel.user_id == uuid.UUID(user_id),
                WorkScheduleModel.is_active.is_(True),
                WorkScheduleModel.effective_from <= check_date,
                sa.or_(
                    WorkScheduleModel.effective_until.is_(None),
                    WorkScheduleModel.effective_until >= check_date,
                ),
            )
            .order_by(WorkScheduleModel.effective_from.desc())
            .limit(1)
        )

        result = await self.session.execute(stmt)
        model: Optional[WorkScheduleModel] = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_summary(model)