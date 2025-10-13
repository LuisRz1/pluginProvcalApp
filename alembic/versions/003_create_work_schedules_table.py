"""create work_schedules table

Revision ID: 003
Revises: 002
Create Date: 2025-01-16 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic.operations import Operations

op: Operations

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'work_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('shift_type', sa.String(50), nullable=False),

        sa.Column('start_time', sa.Time, nullable=False),
        sa.Column('end_time', sa.Time, nullable=False),

        sa.Column('working_days', postgresql.JSON, nullable=False, server_default='[0,1,2,3,4]'),
        sa.Column('late_tolerance_minutes', sa.Integer, nullable=False, server_default='15'),
        sa.Column('break_duration_minutes', sa.Integer, nullable=False, server_default='30'),

        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('effective_from', sa.Date, nullable=False),
        sa.Column('effective_until', sa.Date, nullable=True),

        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.String(500), nullable=True),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )

    # Índices
    op.create_index('idx_work_schedules_user_id', 'work_schedules', ['user_id'])
    op.create_index('idx_work_schedules_is_active', 'work_schedules', ['is_active'])
    op.create_index('idx_work_schedules_user_active', 'work_schedules', ['user_id', 'is_active'])
    op.create_index('idx_work_schedules_dates', 'work_schedules', ['effective_from', 'effective_until'])

    # Constraint para shift_type válidos
    op.create_check_constraint(
        'valid_shift_type',
        'work_schedules',
        "shift_type IN ('morning', 'afternoon', 'night', 'full_day', 'custom')"
    )


def downgrade() -> None:
    op.drop_table('work_schedules')