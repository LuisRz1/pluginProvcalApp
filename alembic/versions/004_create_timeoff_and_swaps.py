"""create time-off, vacation balances and shift swap tables

Revision ID: 003
Revises: 002
Create Date: 2025-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic.operations import Operations

op: Operations

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---------------------------------------------------------------------
    # Tabla: vacation_balances
    # Saldo de vacaciones por usuario/año calendario
    # ---------------------------------------------------------------------
    op.create_table(
        'vacation_balances',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('year', sa.Integer, nullable=False),
        sa.Column('total_days', sa.Integer, nullable=False, server_default='30'),
        sa.Column('used_days', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'year', name='pk_vacation_balances'),
        sa.CheckConstraint('total_days >= 0', name='chk_vacation_balances_total_nonneg'),
        sa.CheckConstraint('used_days >= 0', name='chk_vacation_balances_used_nonneg'),
        sa.CheckConstraint('used_days <= total_days', name='chk_vacation_balances_used_le_total'),
    )
    op.create_index('idx_vacation_balances_user_year', 'vacation_balances', ['user_id', 'year'])

    # ---------------------------------------------------------------------
    # Tabla: time_off_requests
    # Solicitudes de días (vacaciones o permisos) — días completos, calendario
    # ---------------------------------------------------------------------
    op.create_table(
        'time_off_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),         # 'vacation' | 'permission'
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('days_requested', sa.Integer, nullable=False),
        sa.Column('reason', sa.String(500), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),  # 'pending'|'approved'|'rejected'|'cancelled'
        sa.Column('approver_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('decision_at', sa.DateTime(timezone=True), nullable=True),

        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id'], ondelete='SET NULL'),

        sa.CheckConstraint("type IN ('vacation', 'permission')", name='chk_time_off_type'),
        sa.CheckConstraint("status IN ('pending', 'approved', 'rejected', 'cancelled')", name='chk_time_off_status'),
        sa.CheckConstraint('days_requested >= 1', name='chk_time_off_days_ge_1'),
        sa.CheckConstraint('end_date >= start_date', name='chk_time_off_dates_order'),
    )
    op.create_index('idx_time_off_user', 'time_off_requests', ['user_id'])
    op.create_index('idx_time_off_status', 'time_off_requests', ['status'])
    op.create_index('idx_time_off_user_start', 'time_off_requests', ['user_id', 'start_date'])
    op.create_index('idx_time_off_dates', 'time_off_requests', ['start_date', 'end_date'])

    # ---------------------------------------------------------------------
    # Tabla: shift_swap_requests
    # Solicitudes de intercambio de turnos (mismo rol; respuesta del target)
    # ---------------------------------------------------------------------
    op.create_table(
        'shift_swap_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),

        sa.Column('requester_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requester_shift_id', postgresql.UUID(as_uuid=True), nullable=False),

        sa.Column('target_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_shift_id', postgresql.UUID(as_uuid=True), nullable=False),

        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),  # 'pending'|'accepted'|'rejected'|'cancelled'
        sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),

        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['requester_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_user_id'], ['users.id'], ondelete='CASCADE'),
        # Nota: si tu tabla de turnos aún no está migrada, dejamos los shift_id sin FK.
        # Cuando exista (p.ej. horarios_trabajo), puedes añadir FKs en una migración posterior.

        sa.CheckConstraint("status IN ('pending', 'accepted', 'rejected', 'cancelled')", name='chk_shift_swap_status'),
    )
    op.create_index('idx_shift_swap_requester', 'shift_swap_requests', ['requester_user_id'])
    op.create_index('idx_shift_swap_target', 'shift_swap_requests', ['target_user_id'])
    op.create_index('idx_shift_swap_status', 'shift_swap_requests', ['status'])


def downgrade() -> None:
    op.drop_table('shift_swap_requests')
    op.drop_table('time_off_requests')
    op.drop_table('vacation_balances')
