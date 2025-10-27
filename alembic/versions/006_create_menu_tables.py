"""create menu tables

Revision ID: 006_create_menu_tables
Revises: 004_create_timeoff_and_swaps
Create Date: 2025-10-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_create_menu_tables'
down_revision = '004_create_timeoff_and_swaps'
branch_labels = None
depends_on = None

def upgrade():
    # monthly_menus
    op.create_table(
        'monthly_menus',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('year', sa.Integer(), nullable=False, index=True),
        sa.Column('month', sa.Integer(), nullable=False, index=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('source_filename', sa.String(length=255), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('year', 'month', name='uq_monthly_menus_year_month')
    )

    # menu_days
    op.create_table(
        'menu_days',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('menu_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('date', sa.Date(), nullable=False, index=True),
        sa.Column('breakfast', sa.String(length=255), nullable=False, server_default=''),
        sa.Column('lunch', sa.String(length=255), nullable=False, server_default=''),
        sa.Column('dinner', sa.String(length=255), nullable=False, server_default=''),
        sa.Column('is_holiday', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('nutrition_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['menu_id'], ['monthly_menus.id'], name='fk_menu_days_monthly_menus', ondelete='CASCADE'),
        sa.UniqueConstraint('menu_id', 'date', name='uq_menu_days_menu_date')
    )

    # menu_change_requests
    op.create_table(
        'menu_change_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('menu_day_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('day_date', sa.Date(), nullable=False, index=True),
        sa.Column('meal_type', sa.String(length=20), nullable=False),
        sa.Column('old_value', sa.String(length=255), nullable=False, server_default=''),
        sa.Column('new_value', sa.String(length=255), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=False),

        sa.Column('status', sa.String(length=30), nullable=False, index=True, server_default='pending_approval'),
        sa.Column('requested_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('decided_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes_from_decider', sa.String(length=500), nullable=True),

        sa.Column('batch_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),

        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['menu_day_id'], ['menu_days.id'], name='fk_mcr_menu_days', ondelete='CASCADE')
    )

def downgrade():
    op.drop_table('menu_change_requests')
    op.drop_table('menu_days')
    op.drop_table('monthly_menus')
