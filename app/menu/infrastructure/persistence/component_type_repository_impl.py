import uuid
from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column, declarative_base

from app.menu.application.ports.component_type_repository import (
    ComponentTypeRepository,
)
from app.menu.domain.component_type import ComponentType

Base = declarative_base()

class ComponentTypeModel(Base):
    __tablename__ = "component_types"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    component_name: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        unique=True,
    )
    display_order: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "component_name",
            name="uq_component_types_name",
        ),
    )


class PostgreSQLComponentTypeRepository(ComponentTypeRepository):
    """
    Implementación PostgreSQL para la tabla component_types.
    Usa el mismo Base y patrón que el resto de repos de menú.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ==============
    # Helpers internos
    # ==============
    @staticmethod
    def _to_domain(model: ComponentTypeModel) -> ComponentType:
        return ComponentType(
            id=str(model.id),
            name=model.component_name,
            display_order=model.display_order,
        )

    # ==============
    # Métodos del puerto
    # ==============
    async def get_by_name(self, name: str) -> Optional[ComponentType]:
        stmt = (
            select(ComponentTypeModel)
            .where(ComponentTypeModel.component_name == name)
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_all(self) -> List[ComponentType]:
        stmt = (
            select(ComponentTypeModel)
            .order_by(
                ComponentTypeModel.display_order.asc(),
                ComponentTypeModel.component_name.asc(),
            )
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def create(self, component_type: ComponentType) -> ComponentType:
        """
        Crea un nuevo tipo de componente y hace COMMIT
        para que pueda ser referenciado por meal_components.
        """

        # 1. Calcular display_order si no viene
        if component_type.display_order is None:
            stmt = select(sa.func.max(ComponentTypeModel.display_order))
            result = await self._session.execute(stmt)
            max_order = result.scalar() or 0
            component_type.display_order = max_order + 1

        # 2. Resolver el UUID que vamos a guardar
        if component_type.id is None:
            new_id = uuid.uuid4()
        else:
            # si viniera como string, lo convertimos
            new_id = (
                component_type.id
                if isinstance(component_type.id, uuid.UUID)
                else uuid.UUID(str(component_type.id))
            )

        # 3. Insertar y COMMIT
        model = ComponentTypeModel(
            id=new_id,
            component_name=component_type.name,
            display_order=component_type.display_order,
        )

        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)

        # 4. Sincronizar dominio (como string)
        component_type.id = str(model.id)
        component_type.display_order = model.display_order

        return component_type


