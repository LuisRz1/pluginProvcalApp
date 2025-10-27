import uuid
import sqlalchemy as sa
from typing import Optional, List
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, DateTime

from app.menu.application.ports.monthly_menu_repository import MonthlyMenuRepository
from app.menu.domain.monthly_menu import MonthlyMenu
from app.menu.domain.menu_enums import MenuStatus

Base = declarative_base()

class MonthlyMenuModel(Base):
    __tablename__ = "monthly_menus"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    status = Column(String(20), nullable=False, default=MenuStatus.DRAFT.value)
    source_filename = Column(String(255), nullable=True)
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))

class PostgreSQLMonthlyMenuRepository(MonthlyMenuRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, m: MonthlyMenuModel) -> MonthlyMenu:
        return MonthlyMenu(
            id=str(m.id),
            year=m.year,
            month=m.month,
            status=MenuStatus(m.status),
            source_filename=m.source_filename,
            created_by=str(m.created_by) if m.created_by else None,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    async def upsert(self, menu: MonthlyMenu) -> MonthlyMenu:
        if menu.id:
            stmt = select(MonthlyMenuModel).where(MonthlyMenuModel.id == uuid.UUID(menu.id))
            r = await self.session.execute(stmt)
            m = r.scalar_one()
            m.status = menu.status.value
            m.source_filename = menu.source_filename
            m.updated_at = datetime.utcnow()
            await self.session.flush()
            return self._to_domain(m)

        m = MonthlyMenuModel(
            year=menu.year,
            month=menu.month,
            status=menu.status.value,
            source_filename=menu.source_filename,
            created_by=uuid.UUID(menu.created_by) if menu.created_by else None,
        )
        self.session.add(m)
        await self.session.flush()
        return self._to_domain(m)

    async def find_by_year_month(self, year: int, month: int) -> Optional[MonthlyMenu]:
        stmt = select(MonthlyMenuModel).where(MonthlyMenuModel.year == year, MonthlyMenuModel.month == month).limit(1)
        r = await self.session.execute(stmt)
        m = r.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def find_by_id(self, menu_id: str) -> Optional[MonthlyMenu]:
        stmt = select(MonthlyMenuModel).where(MonthlyMenuModel.id == uuid.UUID(menu_id)).limit(1)
        r = await self.session.execute(stmt)
        m = r.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def list_recent(self, limit: int = 12) -> List[MonthlyMenu]:
        stmt = select(MonthlyMenuModel).order_by(MonthlyMenuModel.created_at.desc()).limit(limit)
        r = await self.session.execute(stmt)
        rows = r.scalars().all()
        return [self._to_domain(m) for m in rows]
