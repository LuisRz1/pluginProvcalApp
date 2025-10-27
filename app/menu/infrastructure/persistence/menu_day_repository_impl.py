import uuid
import sqlalchemy as sa
from typing import List, Optional
from datetime import date, datetime

from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import select
from sqlalchemy import Column, Date, String, Boolean, DateTime

from app.menu.application.ports.menu_day_repository import MenuDayRepository
from app.menu.domain.menu_day import MenuDay

Base = declarative_base()

class MenuDayModel(Base):
    __tablename__ = "menu_days"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    breakfast = Column(String(255), nullable=False, default="")
    lunch = Column(String(255), nullable=False, default="")
    dinner = Column(String(255), nullable=False, default="")

    is_holiday = Column(Boolean, nullable=False, server_default=sa.text("false"))
    nutrition_flags = Column(JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))

class PostgreSQLMenuDayRepository(MenuDayRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, m: MenuDayModel) -> MenuDay:
        return MenuDay(
            id=str(m.id),
            menu_id=str(m.menu_id),
            date=m.date,
            breakfast=m.breakfast,
            lunch=m.lunch,
            dinner=m.dinner,
            is_holiday=m.is_holiday,
            nutrition_flags=m.nutrition_flags or {},
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    async def bulk_replace(self, menu_id: str, days: List[MenuDay]) -> None:
        # borra existentes del mes y crea nuevos
        await self.session.execute(sa.text("DELETE FROM menu_days WHERE menu_id = :mid"), {"mid": uuid.UUID(menu_id)})
        for d in days:
            self.session.add(MenuDayModel(
                menu_id=uuid.UUID(menu_id),
                date=d.date,
                breakfast=d.breakfast,
                lunch=d.lunch,
                dinner=d.dinner,
                is_holiday=d.is_holiday,
                nutrition_flags=d.nutrition_flags or {},
            ))
        await self.session.flush()

    async def list_by_menu(self, menu_id: str) -> List[MenuDay]:
        stmt = select(MenuDayModel).where(MenuDayModel.menu_id == uuid.UUID(menu_id)).order_by(MenuDayModel.date.asc())
        r = await self.session.execute(stmt)
        rows = r.scalars().all()
        return [self._to_domain(m) for m in rows]

    async def find_by_menu_and_date(self, menu_id: str, day: date) -> Optional[MenuDay]:
        stmt = select(MenuDayModel).where(
            MenuDayModel.menu_id == uuid.UUID(menu_id),
            MenuDayModel.date == day
        ).limit(1)
        r = await self.session.execute(stmt)
        m = r.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def save(self, day: MenuDay) -> MenuDay:
        if day.id:
            stmt = select(MenuDayModel).where(MenuDayModel.id == uuid.UUID(day.id)).limit(1)
            r = await self.session.execute(stmt)
            m = r.scalar_one()
            m.breakfast = day.breakfast
            m.lunch = day.lunch
            m.dinner = day.dinner
            m.is_holiday = day.is_holiday
            m.nutrition_flags = day.nutrition_flags or {}
            m.updated_at = datetime.utcnow()
            await self.session.flush()
            return self._to_domain(m)

        m = MenuDayModel(
            menu_id=uuid.UUID(day.menu_id),
            date=day.date,
            breakfast=day.breakfast,
            lunch=day.lunch,
            dinner=day.dinner,
            is_holiday=day.is_holiday,
            nutrition_flags=day.nutrition_flags or {},
        )
        self.session.add(m)
        await self.session.flush()
        return self._to_domain(m)

    async def find_by_id(self, menu_day_id: str) -> Optional[MenuDay]:
        stmt = select(MenuDayModel).where(MenuDayModel.id == uuid.UUID(menu_day_id)).limit(1)
        r = await self.session.execute(stmt)
        m = r.scalar_one_or_none()
        return self._to_domain(m) if m else None