"""create attendances table

Revision ID: 002
Revises: 001
Create Date: 2025-01-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic.operations import Operations

op: Operations

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crear tabla attendances"""
    # Crear tabla attendances
    op.create_table(
        'attendances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date, nullable=False),

        # Horarios
        sa.Column('check_in_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('check_out_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scheduled_start_time', sa.Time, nullable=True),  # Viene del WorkSchedule
        sa.Column('scheduled_end_time', sa.Time, nullable=True),

        # Estado
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('type', sa.String(50), nullable=False, server_default='regular'),

        # Geolocalización (JSON)
        sa.Column('check_in_location', postgresql.JSON, nullable=True),
        sa.Column('check_out_location', postgresql.JSON, nullable=True),
        sa.Column('workplace_location', postgresql.JSON, nullable=True),
        sa.Column('workplace_radius_meters', sa.Float, nullable=False, server_default='100.0'),

        # Tardanzas
        sa.Column('is_late', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('late_minutes', sa.Integer, nullable=False, server_default='0'),
        sa.Column('late_tolerance_minutes', sa.Integer, nullable=False, server_default='15'),

        # Regularización
        sa.Column('requires_regularization', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('regularization_notes', sa.String(500), nullable=True),
        sa.Column('regularized_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('regularized_at', sa.DateTime(timezone=True), nullable=True),

        # Descansos (JSON array)
        sa.Column('break_periods', postgresql.JSON, nullable=False, server_default='[]'),

        # Metadatos
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),

        # Foreign keys
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['regularized_by'], ['users.id'], ondelete='SET NULL'),
    )

    # Crear índices
    op.create_index('idx_attendances_user_id', 'attendances', ['user_id'])
    op.create_index('idx_attendances_date', 'attendances', ['date'])
    op.create_index('idx_attendances_user_date', 'attendances', ['user_id', 'date'], unique=True)
    op.create_index('idx_attendances_status', 'attendances', ['status'])
    op.create_index('idx_attendances_requires_regularization', 'attendances', ['requires_regularization'])

    # Check constraints para status y type válidos
    op.create_check_constraint(
        'valid_attendance_status',
        'attendances',
        "status IN ('in_progress', 'on_break', 'completed', 'incomplete', 'pending_regularization')"
    )

    op.create_check_constraint(
        'valid_attendance_type',
        'attendances',
        "type IN ('regular', 'holiday', 'overtime')"
    )


def downgrade() -> None:
    """Eliminar tabla attendances"""
    op.drop_table('attendances')
