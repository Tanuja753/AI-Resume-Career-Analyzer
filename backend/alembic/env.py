from logging.config import fileConfig
import os
import sys
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from app.models.preparation_plan import (
    PreparationPlan,
    PreparationPlanItem,
)

from app.models.preparation_progress import PreparationProgress
from app.models.resume_draft import ResumeDraft
from app.models.generated_resume import GeneratedResume


# Backend directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Add backend to Python path
sys.path.append(str(BASE_DIR))


# Project root
PROJECT_ROOT = BASE_DIR.parent

# Load .env
load_dotenv(PROJECT_ROOT / ".env")


# Alembic configuration
config = context.config


# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Get database settings
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")


if not DB_USER:
    raise ValueError("DB_USER is not set in .env")

if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD is not set in .env")

if not DB_NAME:
    raise ValueError("DB_NAME is not set in .env")


# Build database URL
from sqlalchemy.engine import URL

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)


# Set URL for Alembic
config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.render_as_string(hide_password=False).replace("%", "%%"),
)


# Import SQLAlchemy Base
from app.database.base import Base
from app.models import User


# Metadata used by Alembic
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()