"""
Alembic Migration Environment.

Reads the database URL from application Settings (sync URL, not asyncpg).
Supports both offline and online migration modes.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import get_settings

# Import all models here so Alembic can detect them for autogenerate
from app.models.base import Base  # noqa: F401
# Add future model imports below as models are created:
# from app.models.user import User  # noqa: F401
# from app.models.project import Project  # noqa: F401
# from app.models.paper import Paper  # noqa: F401

settings = get_settings()

# Alembic Config object from alembic.ini
config = context.config

# Override sqlalchemy.url with the sync URL from Settings
# (asyncpg cannot be used by Alembic's synchronous runner)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)

# Set up loggers from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations using an async engine (online mode)."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=settings.DATABASE_URL,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
