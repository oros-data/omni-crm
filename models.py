"""Write your SQLAlchemy tables in this file, below `metadata`; Alembic autogenerate reads it."""

from sqlalchemy import MetaData

metadata = MetaData(
    naming_convention={
        "pk": "%(table_name)s_pkey",
        "uq": "%(table_name)s_%(column_0_N_name)s_key",
        "fk": "%(table_name)s_%(column_0_name)s_fkey",
        "ck": "%(table_name)s_%(constraint_name)s_check",
        "ix": "%(table_name)s_%(column_0_N_name)s_idx",
    }
)
