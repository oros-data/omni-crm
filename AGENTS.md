# AGENTS.md

## Code style
- Write no comments anywhere; the code speaks for itself.
- Write no docstrings anywhere.
- Let names carry the meaning; rename instead of explaining.
- Write functional Python: plain functions and pure helpers.
- Use dataclasses or similar constructs only to categorize data.
- Never repeat yourself; extract a shared helper the second time a pattern appears.

## Schema conventions
- Define every table as SQLAlchemy Core in `models.py`.
- Name tables in plural snake_case.
- Give every table an identity bigint `id` and timestamptz `created_at` and `updated_at`.
- Soft delete through `is_active`; never hard delete.
- Index every foreign key and every column used for filtering.
- Give every synced entity `integration_id` and the CRM's own `ref_id`, unique together.
- Relate deals, contacts, companies and users through N:N link tables.
- Keep link history with `attached_at`, `detached_at` and `is_active`.
- Allow repeated link rows over time, but only one active row per pair.
- Model custom fields as one definition table and one value table per entity.
- Store no normalized type on stages.
- Record deal stage changes in `deal_stage_history`.
- Link activities to user, deal, contact and company through optional foreign keys.
- Model events as an `event_types` catalog plus a `crm_events` log.
- Give `crm_events` `occurred_at`, `entity_type` and `entity_id`, with a unique `event_hash` per integration.

## Migrations
- Edit only `models.py` to change the schema.
- Generate revisions with `alembic revision --autogenerate`.
- Never hand-edit a generated revision beyond what autogenerate cannot express.
- Apply with `alembic upgrade head` on the local Postgres on port 5433.
- Confirm `alembic check` reports no new operations.
- Revisions are numbered sequentially by `migrations/env.py`.

## Setup
- Follow `README.md`.
