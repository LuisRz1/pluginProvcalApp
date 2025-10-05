from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
import sys
from pathlib import Path

from alembic.runtime.environment import EnvironmentContext
from alembic.config import Config
from alembic import context

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from app.shared.config.settings import settings

# this is the Alembic Config object
context: EnvironmentContext
config: Config = context.config

# Convertir la URL async a sync para Alembic
db_url = settings.DATABASE_URL.replace("asyncpg", "psycopg2")

# Configurar la URL de la base de datos desde settings
config.set_main_option('sqlalchemy.url', db_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
from sqlalchemy.orm import declarative_base
Base = declarative_base()

# Importar modelos para que Alembic los reconozca
# IMPORTANTE: Estos imports deben estar después de crear Base
try:
    from app.users.infrastructure.persistence.user_repository_impl import UserModel
    from app.users.infrastructure.persistence.activation_token_repository_impl import ActivationTokenModel

    # Asignar metadata
    UserModel.metadata = Base.metadata
    ActivationTokenModel.metadata = Base.metadata
except ImportError as e:
    print(f"Warning: Could not import models: {e}")

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()