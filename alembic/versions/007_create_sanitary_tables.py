"""create sanitary tables

Revision ID: 007_create_sanitary_tables
Revises: 006_create_menu_tables
Create Date: 2025-12-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic.operations import Operations

op: Operations

# revision identifiers, used by Alembic.
revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crear tablas de sanidad: políticas, tipos de incidencia, empresas y revisiones"""

    # Tabla: sanitary_policies (PoliticaSanidad)
    op.create_table(
        "sanitary_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    # Tabla: sanitary_incident_types (TipoIncidencia)
    op.create_table(
        "sanitary_incident_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "policy_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sanitary_policies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint(
            "policy_id",
            "name",
            name="uq_sanitary_incident_types_policy_name",
        ),
    )

    # Tabla: sanitary_companies (Empresa especializada de sanidad)
    op.create_table(
        "sanitary_companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("business_name", sa.String(200), nullable=False),
        sa.Column("ruc", sa.String(20), nullable=False),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("email", sa.String(150), nullable=True),
        sa.UniqueConstraint("ruc", name="uq_sanitary_companies_ruc"),
    )

    # Tabla: sanitary_reviews (RevisionSanidad)
    op.create_table(
        "sanitary_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "policy_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sanitary_policies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("is_conform", sa.Boolean(), nullable=False),
        sa.Column("observation", sa.Text(), nullable=True),
        sa.Column(
            "incident_type_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sanitary_incident_types.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sanitary_companies.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Eliminar tablas de sanidad (reversión)"""

    op.drop_table("sanitary_reviews")
    op.drop_table("sanitary_companies")
    op.drop_table("sanitary_incident_types")
    op.drop_table("sanitary_policies")
