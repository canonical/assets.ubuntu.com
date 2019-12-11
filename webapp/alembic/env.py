# Standard library
import os
import sys

# Packages
from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Local
sys.path.append(os.getcwd())
from webapp.models import Base  # noqa: E402


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# add your model's MetaData object here
target_metadata = Base.metadata


def get_database_url():
    return os.environ["DATABASE_URL"]


def get_database_session():
    return scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=create_engine(get_database_url()),
        )
    )


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = create_engine(get_database_url())

    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
