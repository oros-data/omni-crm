"""Analytical CRM schema: one SQLAlchemy Core table per entity, read by Alembic autogenerate."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Interval,
    MetaData,
    Numeric,
    Table,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

metadata = MetaData(
    naming_convention={
        "pk": "%(table_name)s_pkey",
        "uq": "%(table_name)s_%(column_0_N_name)s_key",
        "fk": "%(table_name)s_%(column_0_name)s_fkey",
        "ck": "%(table_name)s_%(constraint_name)s_check",
        "ix": "%(table_name)s_%(column_0_N_name)s_idx",
    }
)


def base_columns():
    """UUIDv7 primary key plus created_at and updated_at."""
    return [
        Column("id", UUID(as_uuid=True), primary_key=True, server_default=func.uuidv7()),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
        Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    ]


def synced_columns():
    """Owning integration and the CRM's own id; unique together per table."""
    return [
        Column("integration_id", UUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False),
        Column("ref_id", Text, nullable=False),
    ]


def is_active_column():
    """Soft-delete flag."""
    return Column("is_active", Boolean, nullable=False, server_default=text("true"))


def fk(name, target, nullable=True, ondelete=None):
    """UUID foreign key column."""
    return Column(name, UUID(as_uuid=True), ForeignKey(target, ondelete=ondelete), nullable=nullable)


def link_columns():
    """History columns shared by every N:N link table."""
    return [
        Column("attached_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
        Column("detached_at", DateTime(timezone=True)),
        is_active_column(),
    ]


def active_pair_index(left, right):
    """Allow repeated link rows over time but only one active row per pair."""
    return Index(None, left, right, unique=True, postgresql_where=text("is_active"))


integrations = Table(
    "integrations",
    metadata,
    *base_columns(),
    Column("name", Text, nullable=False),
    Column("provider", Text, nullable=False),
    is_active_column(),
    UniqueConstraint("provider", "name"),
)

users = Table(
    "users",
    metadata,
    *base_columns(),
    *synced_columns(),
    Column("name", Text),
    Column("email", Text),
    Column("phone", Text),
    Column("role", Text),
    Column("team", Text),
    is_active_column(),
    UniqueConstraint("integration_id", "ref_id"),
    Index(None, "email"),
)

pipelines = Table(
    "pipelines",
    metadata,
    *base_columns(),
    *synced_columns(),
    Column("name", Text, nullable=False),
    is_active_column(),
    UniqueConstraint("integration_id", "ref_id"),
)

stages = Table(
    "stages",
    metadata,
    *base_columns(),
    *synced_columns(),
    Column("name", Text, nullable=False),
    Column("position", Integer),
    Column("probability", Numeric(5, 2)),
    fk("pipeline_id", "pipelines.id", nullable=False),
    is_active_column(),
    UniqueConstraint("integration_id", "ref_id"),
    Index(None, "pipeline_id"),
)

contacts = Table(
    "contacts",
    metadata,
    *base_columns(),
    *synced_columns(),
    Column("name", Text),
    Column("email", Text),
    Column("phone", Text),
    Column("source", Text),
    fk("owner_user_id", "users.id"),
    is_active_column(),
    UniqueConstraint("integration_id", "ref_id"),
    Index(None, "email"),
    Index(None, "owner_user_id"),
)

companies = Table(
    "companies",
    metadata,
    *base_columns(),
    *synced_columns(),
    Column("name", Text),
    Column("domain", Text),
    Column("document", Text),
    fk("owner_user_id", "users.id"),
    is_active_column(),
    UniqueConstraint("integration_id", "ref_id"),
    Index(None, "domain"),
    Index(None, "owner_user_id"),
)

deals = Table(
    "deals",
    metadata,
    *base_columns(),
    *synced_columns(),
    Column("title", Text),
    fk("pipeline_id", "pipelines.id"),
    fk("stage_id", "stages.id"),
    fk("owner_user_id", "users.id"),
    Column("amount", Numeric(18, 2)),
    Column("currency", Text),
    Column("status", Text, nullable=False, server_default="open"),
    Column("closed_at", DateTime(timezone=True)),
    Column("lost_reason", Text),
    Column("expected_close_at", DateTime(timezone=True)),
    is_active_column(),
    UniqueConstraint("integration_id", "ref_id"),
    CheckConstraint("status IN ('open', 'won', 'lost')", name="status"),
    Index(None, "pipeline_id"),
    Index(None, "stage_id"),
    Index(None, "owner_user_id"),
    Index(None, "status"),
)

contact_fields = Table(
    "contact_fields",
    metadata,
    *base_columns(),
    *synced_columns(),
    Column("name", Text, nullable=False),
    Column("type", Text),
    Column("options", JSONB),
    is_active_column(),
    UniqueConstraint("integration_id", "ref_id"),
)

contacts_contact_fields = Table(
    "contacts_contact_fields",
    metadata,
    *base_columns(),
    fk("contact_id", "contacts.id", nullable=False, ondelete="CASCADE"),
    fk("contact_field_id", "contact_fields.id", nullable=False, ondelete="CASCADE"),
    Column("value", Text),
    UniqueConstraint("contact_id", "contact_field_id"),
    Index(None, "contact_field_id"),
)

company_fields = Table(
    "company_fields",
    metadata,
    *base_columns(),
    *synced_columns(),
    Column("name", Text, nullable=False),
    Column("type", Text),
    Column("options", JSONB),
    is_active_column(),
    UniqueConstraint("integration_id", "ref_id"),
)

companies_company_fields = Table(
    "companies_company_fields",
    metadata,
    *base_columns(),
    fk("company_id", "companies.id", nullable=False, ondelete="CASCADE"),
    fk("company_field_id", "company_fields.id", nullable=False, ondelete="CASCADE"),
    Column("value", Text),
    UniqueConstraint("company_id", "company_field_id"),
    Index(None, "company_field_id"),
)

deal_fields = Table(
    "deal_fields",
    metadata,
    *base_columns(),
    *synced_columns(),
    Column("name", Text, nullable=False),
    Column("type", Text),
    Column("options", JSONB),
    is_active_column(),
    UniqueConstraint("integration_id", "ref_id"),
)

deals_deal_fields = Table(
    "deals_deal_fields",
    metadata,
    *base_columns(),
    fk("deal_id", "deals.id", nullable=False, ondelete="CASCADE"),
    fk("deal_field_id", "deal_fields.id", nullable=False, ondelete="CASCADE"),
    Column("value", Text),
    UniqueConstraint("deal_id", "deal_field_id"),
    Index(None, "deal_field_id"),
)

deals_contacts = Table(
    "deals_contacts",
    metadata,
    *base_columns(),
    fk("deal_id", "deals.id", nullable=False),
    fk("contact_id", "contacts.id", nullable=False),
    Column("is_primary", Boolean, nullable=False, server_default=text("false")),
    *link_columns(),
    Index(None, "contact_id"),
    active_pair_index("deal_id", "contact_id"),
)

deals_companies = Table(
    "deals_companies",
    metadata,
    *base_columns(),
    fk("deal_id", "deals.id", nullable=False),
    fk("company_id", "companies.id", nullable=False),
    Column("is_primary", Boolean, nullable=False, server_default=text("false")),
    *link_columns(),
    Index(None, "company_id"),
    active_pair_index("deal_id", "company_id"),
)

contacts_companies = Table(
    "contacts_companies",
    metadata,
    *base_columns(),
    fk("contact_id", "contacts.id", nullable=False),
    fk("company_id", "companies.id", nullable=False),
    Column("is_primary", Boolean, nullable=False, server_default=text("false")),
    *link_columns(),
    Index(None, "company_id"),
    active_pair_index("contact_id", "company_id"),
)

deals_users = Table(
    "deals_users",
    metadata,
    *base_columns(),
    fk("deal_id", "deals.id", nullable=False),
    fk("user_id", "users.id", nullable=False),
    *link_columns(),
    Index(None, "user_id"),
    active_pair_index("deal_id", "user_id"),
)

activities = Table(
    "activities",
    metadata,
    *base_columns(),
    *synced_columns(),
    Column("type", Text),
    Column("title", Text),
    Column("description", Text),
    Column("start_at", DateTime(timezone=True)),
    Column("due_at", DateTime(timezone=True)),
    Column("duration", Interval),
    Column("completed_at", DateTime(timezone=True)),
    fk("user_id", "users.id"),
    fk("deal_id", "deals.id"),
    fk("contact_id", "contacts.id"),
    fk("company_id", "companies.id"),
    is_active_column(),
    UniqueConstraint("integration_id", "ref_id"),
    Index(None, "user_id"),
    Index(None, "deal_id"),
    Index(None, "contact_id"),
    Index(None, "company_id"),
    Index(None, "type"),
)

event_types = Table(
    "event_types",
    metadata,
    *base_columns(),
    Column("name", Text, nullable=False),
    is_active_column(),
    UniqueConstraint("name"),
)

crm_events = Table(
    "crm_events",
    metadata,
    *base_columns(),
    Column("integration_id", UUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False),
    fk("event_type_id", "event_types.id", nullable=False),
    Column("event_hash", Text, nullable=False),
    Column("occurred_at", DateTime(timezone=True), nullable=False),
    Column("entity_type", Text),
    Column("entity_id", UUID(as_uuid=True)),
    fk("actor_user_id", "users.id"),
    Column("properties", JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    UniqueConstraint("integration_id", "event_hash"),
    Index(None, "event_type_id", "occurred_at"),
    Index(None, "entity_type", "entity_id"),
    Index(None, "actor_user_id"),
)

deal_stage_history = Table(
    "deal_stage_history",
    metadata,
    *base_columns(),
    fk("deal_id", "deals.id", nullable=False, ondelete="CASCADE"),
    fk("stage_id", "stages.id", nullable=False),
    Column("entered_at", DateTime(timezone=True), nullable=False),
    Column("left_at", DateTime(timezone=True)),
    fk("crm_event_id", "crm_events.id"),
    Index(None, "deal_id", "entered_at"),
    Index(None, "stage_id"),
)
