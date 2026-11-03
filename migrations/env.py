"""Alembic environment: reads DATABASE_URL, targets models.metadata and numbers new revisions sequentially."""

import os
import re

from alembic import context
from sqlalchemy import create_engine, pool

from models import metadata

DEFAULT_URL = "postgresql+psycopg://omni_crm:omni_crm@127.0.0.1:5433/omni_crm"
REVISION_ID = re.compile(r"[0-9]{4}")


def get_url():
    """Return DATABASE_URL from the environment or the local compose default."""
    return os.environ.get("DATABASE_URL", DEFAULT_URL)


def next_revision_id(head):
    """Return the four digit id that follows head, or 0001 when there is no head yet."""
    if head is None:
        return "0001"
    if not isinstance(head, str) or not REVISION_ID.fullmatch(head):
        raise ValueError(f"cannot number the next migration after head {head!r}: expected a four digit id such as '0002'")
    return f"{int(head) + 1:04d}"


def number_revision(migration_context, revision, directives):
    """Give a newly generated revision the next sequential id unless --rev-id was passed."""
    if getattr(context.config.cmd_opts, "rev_id", None):
        return
    for script in directives:
        heads = [head.revision for head in context.script.get_revisions(script.head or "head") if head is not None]
        script.rev_id = next_revision_id(heads[0] if heads else None)


def run_migrations_offline():
    """Emit migration SQL without connecting to the database."""
    context.configure(
        url=get_url(),
        target_metadata=metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        process_revision_directives=number_revision,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations against a live database connection."""
    engine = create_engine(
        get_url(),
        poolclass=pool.NullPool,
        connect_args={"options": "-c timezone=UTC"},
    )
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=metadata,
            compare_type=True,
            process_revision_directives=number_revision,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
