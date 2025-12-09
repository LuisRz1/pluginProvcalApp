"""create menu tables

Revision ID: 006_create_menu_tables
Revises: 004_create_timeoff_and_swaps
Create Date: 2025-10-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "006"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    # =========================
    # monthly_menus
    # =========================
    op.create_table(
        "monthly_menus",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("year", sa.Integer(), nullable=False, index=True),
        sa.Column("month", sa.Integer(), nullable=False, index=True),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("source_filename", sa.String(length=255), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("year", "month", name="uq_monthly_menus_year_month"),
    )

    # =========================
    # weekly_menus
    # =========================
    op.create_table(
        "weekly_menus",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "monthly_menu_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column("week_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["monthly_menu_id"],
            ["monthly_menus.id"],
            name="fk_weekly_menus_monthly_menus",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "monthly_menu_id",
            "week_number",
            name="uq_weekly_menus_month_week",
        ),
    )

    # =========================
    # daily_menus  (reemplaza la idea de menu_days)
    # =========================
    op.create_table(
        "daily_menus",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "weekly_menu_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column("date", sa.Date(), nullable=False, index=True),
        sa.Column("day_of_week", sa.String(length=20), nullable=True),
        sa.Column(
            "is_holiday",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "nutrition_flags",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["weekly_menu_id"],
            ["weekly_menus.id"],
            name="fk_daily_menus_weekly_menus",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("weekly_menu_id", "date", name="uq_daily_menus_week_date"),
    )

    # =========================
    # component_types (Entrada, Fondo, Refresco, etc.)
    # =========================
    op.create_table(
        "component_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("component_name", sa.String(length=100), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.UniqueConstraint("component_name", name="uq_component_types_name"),
    )

    # =========================
    # meals (Desayuno / Almuerzo / Cena por día)
    # =========================
    op.create_table(
        "meals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "daily_menu_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column("meal_type", sa.String(length=20), nullable=False),
        sa.Column("total_kcal", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["daily_menu_id"],
            ["daily_menus.id"],
            name="fk_meals_daily_menus",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("daily_menu_id", "meal_type", name="uq_meals_daily_type"),
    )

    # =========================
    # meal_components (platos dentro de cada comida)
    # =========================
    op.create_table(
        "meal_components",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "meal_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "component_type_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column("dish_name", sa.String(length=255), nullable=False),
        sa.Column("calories", sa.Float(), nullable=True),
        sa.Column(
            "order_position",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.ForeignKeyConstraint(
            ["meal_id"],
            ["meals.id"],
            name="fk_meal_components_meals",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["component_type_id"],
            ["component_types.id"],
            name="fk_meal_components_component_types",
            ondelete="RESTRICT",
        ),
    )

    # =========================
    # menu_change_requests (ahora cuelga de daily_menus)
    # =========================
    op.create_table(
        "menu_change_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "daily_menu_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column("day_date", sa.Date(), nullable=False, index=True),
        sa.Column("meal_type", sa.String(length=20), nullable=False),
        sa.Column(
            "old_value",
            sa.String(length=255),
            nullable=False,
            server_default="",
        ),
        sa.Column("new_value", sa.String(length=255), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            index=True,
            server_default="pending_approval",
        ),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decided_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes_from_decider", sa.String(length=500), nullable=True),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["daily_menu_id"],
            ["daily_menus.id"],
            name="fk_mcr_daily_menus",
            ondelete="CASCADE",
        ),
    )


def downgrade():
    op.drop_table("menu_change_requests")
    op.drop_table("meal_components")
    op.drop_table("meals")
    op.drop_table("component_types")
    op.drop_table("daily_menus")
    op.drop_table("weekly_menus")
    op.drop_table("monthly_menus")
