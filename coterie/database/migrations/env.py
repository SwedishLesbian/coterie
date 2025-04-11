"""Alembic environment configuration for Coterie database migrations.

This module configures the Alembic migration environment, setting up the database
connection and migration context for both offline and online migrations.
"""

from logging.config import fileConfig
from typing import Optional

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from coterie.database.engine import DB_PATH
from coterie.models.base import Base
from coterie.models.character import Character
from coterie.models.chronicle import Chronicle, GameSession
from coterie.models.player import Player
from coterie.models.staff import Staff
from coterie.models.trait import Trait
from coterie.models.vampire import Vampire, Discipline, Ritual, Bond

# Import all models that should be included in migrations here
# This is necessary for Alembic to detect model changes
__all__ = [
    'Character', 'Chronicle', 'GameSession', 'Player', 'Staff', 'Trait',
    'Vampire', 'Discipline', 'Ritual', 'Bond'
]

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with our actual database URL
config.set_main_option('sqlalchemy.url', f'sqlite:///{DB_PATH}')

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
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
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 