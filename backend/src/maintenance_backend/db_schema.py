"""Shared SQLAlchemy schema objects for migrations and DB tooling."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


metadata = sa.MetaData()

equipment_status_enum = postgresql.ENUM(
    "normal",
    "warning",
    "critical",
    "unknown",
    name="equipment_status",
)
actor_role_enum = postgresql.ENUM(
    "admin",
    "engineer",
    "operator",
    "user",
    name="actor_role",
)
channel_enum = postgresql.ENUM("telegram", "web", name="channel")
data_source_type_enum = postgresql.ENUM(
    "manual",
    "external_monitoring",
    "import",
    "backend_derived",
    name="data_source_type",
)
review_status_enum = postgresql.ENUM(
    "pending",
    "reviewed",
    "resolved",
    name="review_status",
)

system_actors = sa.Table(
    "system_actors",
    metadata,
    sa.Column("actor_id", sa.Text(), primary_key=True),
    sa.Column("external_id", sa.Text(), nullable=False),
    sa.Column("display_name", sa.Text()),
    sa.Column("role", actor_role_enum, nullable=False),
    sa.Column("activity_scope", sa.Text()),
    sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Index("ix_system_actors_external_id", "external_id", unique=True),
    sa.Index("ix_system_actors_role_is_active", "role", "is_active"),
)

locations = sa.Table(
    "locations",
    metadata,
    sa.Column("location_id", sa.Text(), primary_key=True),
    sa.Column("name", sa.Text(), nullable=False),
    sa.Column("location_type", sa.Text(), nullable=False),
    sa.Column("parent_location_id", sa.Text(), sa.ForeignKey("locations.location_id")),
    sa.Column(
        "display_order", sa.Integer(), nullable=False, server_default=sa.text("0")
    ),
    sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Index("ix_locations_parent_location_id", "parent_location_id"),
    sa.Index("ix_locations_location_type_is_active", "location_type", "is_active"),
)

equipment = sa.Table(
    "equipment",
    metadata,
    sa.Column("equipment_id", sa.Text(), primary_key=True),
    sa.Column("name", sa.Text(), nullable=False),
    sa.Column("equipment_code", sa.Text()),
    sa.Column(
        "location_id", sa.Text(), sa.ForeignKey("locations.location_id"), nullable=False
    ),
    sa.Column("owner_actor_id", sa.Text(), sa.ForeignKey("system_actors.actor_id")),
    sa.Column(
        "current_status",
        equipment_status_enum,
        nullable=False,
        server_default=sa.text("'unknown'::equipment_status"),
    ),
    sa.Column("maintenance_due_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("maintenance_completed_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Index("ix_equipment_location_id", "location_id"),
    sa.Index("ix_equipment_owner_actor_id", "owner_actor_id"),
    sa.Index("ix_equipment_current_status_is_active", "current_status", "is_active"),
    sa.Index(
        "ix_equipment_equipment_code_not_null",
        "equipment_code",
        unique=True,
        postgresql_where=sa.text("equipment_code IS NOT NULL"),
    ),
)

data_sources = sa.Table(
    "data_sources",
    metadata,
    sa.Column("source_id", sa.Text(), primary_key=True),
    sa.Column("source_type", data_source_type_enum, nullable=False),
    sa.Column("name", sa.Text(), nullable=False),
    sa.Column("origin_semantics", sa.Text()),
    sa.Column("trust_semantics", sa.Text()),
    sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.UniqueConstraint(
        "source_type",
        "name",
        name="uq_data_sources_source_type_name",
    ),
    sa.Index("ix_data_sources_source_type", "source_type"),
)

sensors = sa.Table(
    "sensors",
    metadata,
    sa.Column("sensor_id", sa.Text(), primary_key=True),
    sa.Column(
        "equipment_id",
        sa.Text(),
        sa.ForeignKey("equipment.equipment_id"),
        nullable=False,
    ),
    sa.Column("name", sa.Text(), nullable=False),
    sa.Column("sensor_type", sa.Text(), nullable=False),
    sa.Column("data_source_id", sa.Text(), sa.ForeignKey("data_sources.source_id")),
    sa.Column(
        "is_primary_for_state", sa.Boolean(), nullable=False, server_default=sa.false()
    ),
    sa.Column("last_observed_at", sa.DateTime(timezone=True)),
    sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.UniqueConstraint("equipment_id", "name", name="uq_sensors_equipment_id_name"),
    sa.Index("ix_sensors_equipment_id", "equipment_id"),
    sa.Index("ix_sensors_data_source_id", "data_source_id"),
    sa.Index("ix_sensors_sensor_type_is_active", "sensor_type", "is_active"),
)

sensor_groups = sa.Table(
    "sensor_groups",
    metadata,
    sa.Column("sensor_group_id", sa.Text(), primary_key=True),
    sa.Column(
        "equipment_id",
        sa.Text(),
        sa.ForeignKey("equipment.equipment_id"),
        nullable=False,
    ),
    sa.Column("name", sa.Text(), nullable=False),
    sa.Column("group_type", sa.Text(), nullable=False),
    sa.Column("data_source_id", sa.Text(), sa.ForeignKey("data_sources.source_id")),
    sa.Column(
        "is_used_for_state_assessment",
        sa.Boolean(),
        nullable=False,
        server_default=sa.false(),
    ),
    sa.Column("image_url", sa.Text(), nullable=True),
    sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.UniqueConstraint(
        "equipment_id",
        "name",
        name="uq_sensor_groups_equipment_id_name",
    ),
    sa.Index("ix_sensor_groups_equipment_id", "equipment_id"),
    sa.Index("ix_sensor_groups_data_source_id", "data_source_id"),
    sa.Index("ix_sensor_groups_group_type_is_active", "group_type", "is_active"),
)

sensor_group_members = sa.Table(
    "sensor_group_members",
    metadata,
    sa.Column(
        "sensor_group_id",
        sa.Text(),
        sa.ForeignKey("sensor_groups.sensor_group_id"),
        primary_key=True,
    ),
    sa.Column(
        "sensor_id", sa.Text(), sa.ForeignKey("sensors.sensor_id"), primary_key=True
    ),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Index("ix_sensor_group_members_sensor_id", "sensor_id"),
)

equipment_state_snapshots = sa.Table(
    "equipment_state_snapshots",
    metadata,
    sa.Column("snapshot_id", sa.Text(), primary_key=True),
    sa.Column(
        "equipment_id",
        sa.Text(),
        sa.ForeignKey("equipment.equipment_id"),
        nullable=False,
    ),
    sa.Column("status", equipment_status_enum, nullable=False),
    sa.Column("severity", sa.Text()),
    sa.Column("summary", sa.Text()),
    sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column(
        "data_source_id",
        sa.Text(),
        sa.ForeignKey("data_sources.source_id"),
        nullable=False,
    ),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Index("ix_equipment_state_snapshots_equipment_id", "equipment_id"),
    sa.Index("ix_equipment_state_snapshots_data_source_id", "data_source_id"),
    sa.Index(
        "ix_equipment_state_snapshots_equipment_effective_at_desc",
        "equipment_id",
        sa.text("effective_at DESC"),
    ),
    sa.Index(
        "ix_equipment_state_snapshots_status_effective_at_desc",
        "status",
        sa.text("effective_at DESC"),
    ),
)

equipment_state_snapshot_sensors = sa.Table(
    "equipment_state_snapshot_sensors",
    metadata,
    sa.Column(
        "snapshot_id",
        sa.Text(),
        sa.ForeignKey("equipment_state_snapshots.snapshot_id"),
        primary_key=True,
    ),
    sa.Column(
        "sensor_id", sa.Text(), sa.ForeignKey("sensors.sensor_id"), primary_key=True
    ),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Index("ix_equipment_state_snapshot_sensors_sensor_id", "sensor_id"),
)

equipment_state_snapshot_sensor_groups = sa.Table(
    "equipment_state_snapshot_sensor_groups",
    metadata,
    sa.Column(
        "snapshot_id",
        sa.Text(),
        sa.ForeignKey("equipment_state_snapshots.snapshot_id"),
        primary_key=True,
    ),
    sa.Column(
        "sensor_group_id",
        sa.Text(),
        sa.ForeignKey("sensor_groups.sensor_group_id"),
        primary_key=True,
    ),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Index(
        "ix_equipment_state_snapshot_sensor_groups_sensor_group_id",
        "sensor_group_id",
    ),
)

equipment_state_records = sa.Table(
    "equipment_state_records",
    metadata,
    sa.Column("record_id", sa.Text(), primary_key=True),
    sa.Column(
        "equipment_id",
        sa.Text(),
        sa.ForeignKey("equipment.equipment_id"),
        nullable=False,
    ),
    sa.Column(
        "author_actor_id",
        sa.Text(),
        sa.ForeignKey("system_actors.actor_id"),
        nullable=False,
    ),
    sa.Column("channel", channel_enum, nullable=False),
    sa.Column("status", equipment_status_enum, nullable=False),
    sa.Column("comment", sa.Text()),
    sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("source_type", data_source_type_enum, nullable=False),
    sa.Column(
        "review_status",
        review_status_enum,
        nullable=False,
        server_default=sa.text("'pending'::review_status"),
    ),
    sa.Column(
        "reviewed_by_actor_id", sa.Text(), sa.ForeignKey("system_actors.actor_id")
    ),
    sa.Column("reviewed_at", sa.DateTime(timezone=True)),
    sa.Column("review_comment", sa.Text()),
    sa.Column("idempotency_key", sa.Text()),
    sa.Column("payload_hash", sa.Text()),
    sa.Index("ix_equipment_state_records_equipment_id", "equipment_id"),
    sa.Index("ix_equipment_state_records_author_actor_id", "author_actor_id"),
    sa.Index(
        "ix_equipment_state_records_reviewed_by_actor_id",
        "reviewed_by_actor_id",
    ),
    sa.Index(
        "ix_equipment_state_records_equipment_observed_at_desc",
        "equipment_id",
        sa.text("observed_at DESC"),
    ),
    sa.Index(
        "ix_equipment_state_records_review_status_created_at_desc",
        "review_status",
        sa.text("created_at DESC"),
    ),
    sa.Index(
        "ix_equipment_state_records_idempotency_key_not_null",
        "idempotency_key",
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    ),
)

equipment_state_record_sensors = sa.Table(
    "equipment_state_record_sensors",
    metadata,
    sa.Column(
        "record_id",
        sa.Text(),
        sa.ForeignKey("equipment_state_records.record_id"),
        primary_key=True,
    ),
    sa.Column(
        "sensor_id", sa.Text(), sa.ForeignKey("sensors.sensor_id"), primary_key=True
    ),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Index("ix_equipment_state_record_sensors_sensor_id", "sensor_id"),
)

equipment_state_record_sensor_groups = sa.Table(
    "equipment_state_record_sensor_groups",
    metadata,
    sa.Column(
        "record_id",
        sa.Text(),
        sa.ForeignKey("equipment_state_records.record_id"),
        primary_key=True,
    ),
    sa.Column(
        "sensor_group_id",
        sa.Text(),
        sa.ForeignKey("sensor_groups.sensor_group_id"),
        primary_key=True,
    ),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Index(
        "ix_equipment_state_record_sensor_groups_sensor_group_id",
        "sensor_group_id",
    ),
)

knowledge_items = sa.Table(
    "knowledge_items",
    metadata,
    sa.Column("knowledge_item_id", sa.Text(), primary_key=True),
    sa.Column("title", sa.Text(), nullable=False),
    sa.Column("body", sa.Text(), nullable=False),
    sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Index("ix_knowledge_items_is_active", "is_active"),
)

knowledge_item_equipment_types = sa.Table(
    "knowledge_item_equipment_types",
    metadata,
    sa.Column(
        "knowledge_item_id",
        sa.Text(),
        sa.ForeignKey("knowledge_items.knowledge_item_id"),
        primary_key=True,
    ),
    sa.Column("equipment_type", sa.Text(), primary_key=True),
)

knowledge_item_sensor_types = sa.Table(
    "knowledge_item_sensor_types",
    metadata,
    sa.Column(
        "knowledge_item_id",
        sa.Text(),
        sa.ForeignKey("knowledge_items.knowledge_item_id"),
        primary_key=True,
    ),
    sa.Column("sensor_type", sa.Text(), primary_key=True),
)

knowledge_item_sensor_group_types = sa.Table(
    "knowledge_item_sensor_group_types",
    metadata,
    sa.Column(
        "knowledge_item_id",
        sa.Text(),
        sa.ForeignKey("knowledge_items.knowledge_item_id"),
        primary_key=True,
    ),
    sa.Column("sensor_group_type", sa.Text(), primary_key=True),
)

ALL_TABLES = (
    system_actors,
    locations,
    equipment,
    data_sources,
    sensors,
    sensor_groups,
    sensor_group_members,
    equipment_state_snapshots,
    equipment_state_snapshot_sensors,
    equipment_state_snapshot_sensor_groups,
    equipment_state_records,
    equipment_state_record_sensors,
    equipment_state_record_sensor_groups,
    knowledge_items,
    knowledge_item_equipment_types,
    knowledge_item_sensor_types,
    knowledge_item_sensor_group_types,
)

TABLES_BY_NAME = {table.name: table for table in ALL_TABLES}
