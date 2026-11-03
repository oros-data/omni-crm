# omni-crm

Empty Alembic + Postgres setup: write SQLAlchemy models, let Alembic generate the migrations.

## Prerequisites
Docker with Compose, Python 3.11+.

## Setup
```bash
docker compose up -d
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
Postgres listens on `127.0.0.1:5433` (not 5432, which your other projects may already use). User, password and database are all `omni_crm`.

## Write models
Edit `models.py` and add tables under `metadata`, for example:
```python
# from sqlalchemy import Column, Integer, Text, Table
# users = Table("users", metadata, Column("id", Integer, primary_key=True), Column("name", Text, nullable=False))
```

## Migrations
```bash
alembic revision --autogenerate -m "create users"   # creates migrations/versions/0001_create_users.py
alembic upgrade head
alembic downgrade -1
alembic upgrade head --sql                          # print the SQL only
alembic current
```

## psql
```bash
docker compose exec postgres psql -U omni_crm -d omni_crm
```

## Reset
```bash
docker compose down -v    # deletes the database; delete migrations/versions/0*.py too to start over
```

## Change port or URL
- Port: `POSTGRES_PORT=5434 docker compose up -d`, then `export DATABASE_URL=postgresql+psycopg://omni_crm:omni_crm@127.0.0.1:5434/omni_crm`.
- Any database: set `DATABASE_URL` (default `postgresql+psycopg://omni_crm:omni_crm@127.0.0.1:5433/omni_crm`).
