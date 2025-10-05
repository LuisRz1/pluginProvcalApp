"""create users and activation tokens tables

Revision ID: 001
Revises:
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic.operations import Operations

op: Operations

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

user_role_enum = postgresql.ENUM(
    'employee', 'cook', 'nutritionist', 'warehouse', 'admin',
    name='userrole'
)
user_status_enum = postgresql.ENUM(
    'pending_activation', 'active', 'inactive', 'suspended',
    name='userstatus'
)

def upgrade() -> None:

    # Crear tabla users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('employee_id', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('personal_email', sa.String(255), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        #sa.Column('role', user_role_enum, nullable=False),
        #sa.Column('status', user_status_enum, nullable=False, server_default='pending_activation'),

        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('dni', sa.String(20), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('address', sa.String(500), nullable=True),

        sa.Column('data_processing_consent', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('data_processing_consent_date', sa.DateTime(timezone=True), nullable=True),

        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('activated_at', sa.DateTime(timezone=True), nullable=True),

        sa.Column('previous_passwords', postgresql.JSON, nullable=False, server_default='[]'),
    )

    # Validaciones para role y status
    op.create_check_constraint(
        'valid_role',
        'users',
        "role IN ('employee', 'cook', 'nutritionist', 'warehouse', 'admin')"
    )

    # Crear índices adicionales para users
    op.create_index('idx_users_employee_id', 'users', ['employee_id'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_status', 'users', ['status'])
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_dni', 'users', ['dni'])

    # Crear tabla activation_tokens
    op.create_table(
        'activation_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('token', sa.String(255), nullable=False, unique=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', sa.String(50), nullable=False),

        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_used', sa.Boolean, nullable=False, server_default='false'),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Crear índices para activation_tokens
    op.create_index('idx_activation_tokens_token', 'activation_tokens', ['token'])
    op.create_index('idx_activation_tokens_user_id', 'activation_tokens', ['user_id'])
    op.create_index('idx_activation_tokens_is_used', 'activation_tokens', ['is_used'])
    op.create_index('idx_activation_tokens_expires_at', 'activation_tokens', ['expires_at'])


def downgrade() -> None:
    # Eliminar tablas
    op.drop_table('activation_tokens')
    op.drop_table('users')

    # Eliminar enums
    op.execute('DROP TYPE IF EXISTS userstatus')
    op.execute('DROP TYPE IF EXISTS userrole')