import uuid
import sqlalchemy as sa
from typing import List, Optional
from datetime import date, datetime

from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import select
from sqlalchemy import Column, Date, String, Boolean, DateTime, text

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
        self.session_factory = async_sessionmaker(bind=session.bind, expire_on_commit=False)

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

    async def bulk_replace(self, menu_id: str, days: list[MenuDay]) -> None:
        mid = uuid.UUID(menu_id)
        async with self.session_factory() as session:
            async with session.begin():
                # 1) borrar los existentes del mes/menú
                await session.execute(
                    text("DELETE FROM menu_days WHERE menu_id = :mid"),
                    {"mid": mid},
                )

                if not days:
                    return

                # 2) insertar/actualizar en bloque
                payload = []
                for d in days:
                    did = uuid.UUID(d.id) if d.id else uuid.uuid4()
                    payload.append({
                        "id": did,  # UUID
                        "menu_id": mid,
                        "date": d.date,  # DATE (no string)
                        "breakfast": d.breakfast or "",
                        "lunch": d.lunch or "",
                        "dinner": d.dinner or "",
                        "is_holiday": bool(d.is_holiday),
                        "created_at": d.created_at,
                        "updated_at": d.updated_at,
                    })

                stmt = pg_insert(MenuDayModel).values(payload)
                stmt = stmt.on_conflict_do_update(
                    index_elements=[MenuDayModel.id],  # o (menu_id,date) si lo tienes único
                    set_={
                        "breakfast": stmt.excluded.breakfast,
                        "lunch": stmt.excluded.lunch,
                        "dinner": stmt.excluded.dinner,
                        "is_holiday": stmt.excluded.is_holiday,
                        "updated_at": text("now()"),
                    },
                )
                await session.execute(stmt)

    async def list_by_menu(self, menu_id: str) -> List[MenuDay]:
        stmt = select(MenuDayModel).where(MenuDayModel.menu_id == uuid.UUID(str(menu_id))).order_by(MenuDayModel.date.asc())
        r = await self.session.execute(stmt)
        rows = r.scalars().all()
        return [self._to_domain(m) for m in rows]

    async def list_for_month(self, year: int, month: int) -> list[MenuDay]:
        async with self.session_factory() as session:
            q = select(MenuDayModel).where(
                text("EXTRACT(YEAR FROM date) = :y AND EXTRACT(MONTH FROM date) = :m")
            ).params(y=year, m=month).order_by(MenuDayModel.date.asc())
            r = await session.execute(q)
            rows = r.scalars().all()

            out: list[MenuDay] = []
            for m in rows:
                out.append(MenuDay(
                    id=m.id,
                    menu_id=str(m.menu_id),
                    date=m.date,
                    breakfast=m.breakfast,
                    lunch=m.lunch,
                    dinner=m.dinner,
                    is_holiday=bool(m.is_holiday),
                    created_at=m.created_at,
                    updated_at=m.updated_at,
                ))
            return out

    async def find_by_menu_and_date(self, menu_id: str, day: date) -> Optional[MenuDay]:
        stmt = select(MenuDayModel).where(
            MenuDayModel.menu_id == uuid.UUID(menu_id),
            MenuDayModel.date == day
        ).limit(1)
        r = await self.session.execute(stmt)
        m = r.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def save(self, day: MenuDay) -> MenuDay:
        table = MenuDayModel.__table__

        values = dict(
            id=uuid.UUID(day.id) if day.id else uuid.uuid4(),
            menu_id=uuid.UUID(day.menu_id) if isinstance(day.menu_id, str) else day.menu_id,
            date=day.date,
            breakfast=day.breakfast,
            lunch=day.lunch,
            dinner=day.dinner,
            is_holiday=day.is_holiday,
            nutrition_flags=day.nutrition_flags or {},
            created_at=day.created_at,
            updated_at=day.updated_at,
        )

        stmt = pg_insert(table).values(values)
        stmt = stmt.on_conflict_do_update(
            # UNIQUE(menu_id, date)
            index_elements=[table.c.menu_id, table.c.date],
            set_={
                "breakfast": stmt.excluded.breakfast,
                "lunch": stmt.excluded.lunch,
                "dinner": stmt.excluded.dinner,
                "is_holiday": stmt.excluded.is_holiday,
                "nutrition_flags": stmt.excluded.nutrition_flags,
                "updated_at": sa.func.now(),
            },
        ).returning(*table.c)

        res = await self.session.execute(stmt)
        row = res.first()
        await self.session.commit()

        m = row[0] if hasattr(row, "__getitem__") else row
        return self._to_domain(m)

    async def find_by_id(self, menu_day_id: str) -> Optional[MenuDay]:
        stmt = select(MenuDayModel).where(MenuDayModel.id == uuid.UUID(str(menu_day_id))).limit(1)
        r = await self.session.execute(stmt)
        m = r.scalar_one_or_none()
        return self._to_domain(m) if m else None