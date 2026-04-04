"""Baseline core domain schema."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260404_0001"
down_revision = None
branch_labels = None
depends_on = None


equipment_status = postgresql.ENUM(
    "normal",
    "warning",
    "critical",
    "unknown",
    name="equipment_status",
    create_type=False,
)
actor_role = postgresql.ENUM(
    "admin",
    "engineer",
    "operator",
    "user",
    name="actor_role",
    create_type=False,
)
channel = postgresql.ENUM(
    "telegram",
    "web",
    name="channel",
    create_type=False,
)
data_source_type = postgresql.ENUM(
    "manual",
    "external_monitoring",
    "import",
    "backend_derived",
    name="data_source_type",
    create_type=False,
)
review_status = postgresql.ENUM(
    "pending",
    "reviewed",
    "resolved",
    name="review_status",
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""

    bind = op.get_bind()
    for enum_type in (
        equipment_status,
        actor_role,
        channel,
        data_source_type,
        review_status,
    ):
        enum_type.create(bind, checkfirst=True)

    op.create_table(
        "system_actors",
        sa.Column("actor_id", sa.Text(), nullable=False),
        sa.Column("external_id", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.Column("role", actor_role, nullable=False),
        sa.Column("activity_scope", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("actor_id"),
    )
    op.create_index(
        "ix_system_actors_external_id",
        "system_actors",
        ["external_id"],
        unique=True,
    )
    op.create_index(
        "ix_system_actors_role_is_active",
        "system_actors",
        ["role", "is_active"],
        unique=False,
    )

    op.create_table(
        "locations",
        sa.Column("location_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("location_type", sa.Text(), nullable=False),
        sa.Column("parent_location_id", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["parent_location_id"], ["locations.location_id"]),
        sa.PrimaryKeyConstraint("location_id"),
    )
    op.create_index(
        "ix_locations_parent_location_id",
        "locations",
        ["parent_location_id"],
        unique=False,
    )
    op.create_index(
        "ix_locations_location_type_is_active",
        "locations",
        ["location_type", "is_active"],
        unique=False,
    )

    op.create_table(
        "data_sources",
        sa.Column("source_id", sa.Text(), nullable=False),
        sa.Column("source_type", data_source_type, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("origin_semantics", sa.Text(), nullable=True),
        sa.Column("trust_semantics", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("source_id"),
        sa.UniqueConstraint("source_type", "name", name="uq_data_sources_source_type_name"),
    )
    op.create_index(
        "ix_data_sources_source_type",
        "data_sources",
        ["source_type"],
        unique=False,
    )

    op.create_table(
        "equipment",
        sa.Column("equipment_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("equipment_code", sa.Text(), nullable=True),
        sa.Column("location_id", sa.Text(), nullable=False),
        sa.Column("owner_actor_id", sa.Text(), nullable=True),
        sa.Column(
            "current_status",
            equipment_status,
            server_default=sa.text("'unknown'::equipment_status"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["location_id"], ["locations.location_id"]),
        sa.ForeignKeyConstraint(["owner_actor_id"], ["system_actors.actor_id"]),
        sa.PrimaryKeyConstraint("equipment_id"),
    )
    op.create_index("ix_equipment_location_id", "equipment", ["location_id"], unique=False)
    op.create_index(
        "ix_equipment_owner_actor_id",
        "equipment",
        ["owner_actor_id"],
        unique=False,
    )
    op.create_index(
        "ix_equipment_current_status_is_active",
        "equipment",
        ["current_status", "is_active"],
        unique=False,
    )
    op.create_index(
        "ix_equipment_equipment_code_not_null",
        "equipment",
        ["equipment_code"],
        unique=True,
        postgresql_where=sa.text("equipment_code IS NOT NULL"),
    )

    op.create_table(
        "sensors",
        sa.Column("sensor_id", sa.Text(), nullable=False),
        sa.Column("equipment_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("sensor_type", sa.Text(), nullable=False),
        sa.Column("data_source_id", sa.Text(), nullable=True),
        sa.Column(
            "is_primary_for_state",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column("last_observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_sources.source_id"]),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.equipment_id"]),
        sa.PrimaryKeyConstraint("sensor_id"),
        sa.UniqueConstraint("equipment_id", "name", name="uq_sensors_equipment_id_name"),
    )
    op.create_index("ix_sensors_equipment_id", "sensors", ["equipment_id"], unique=False)
    op.create_index(
        "ix_sensors_data_source_id",
        "sensors",
        ["data_source_id"],
        unique=False,
    )
    op.create_index(
        "ix_sensors_sensor_type_is_active",
        "sensors",
        ["sensor_type", "is_active"],
        unique=False,
    )

    op.create_table(
        "sensor_groups",
        sa.Column("sensor_group_id", sa.Text(), nullable=False),
        sa.Column("equipment_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("group_type", sa.Text(), nullable=False),
        sa.Column("data_source_id", sa.Text(), nullable=True),
        sa.Column(
            "is_used_for_state_assessment",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_sources.source_id"]),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.equipment_id"]),
        sa.PrimaryKeyConstraint("sensor_group_id"),
        sa.UniqueConstraint(
            "equipment_id",
            "name",
            name="uq_sensor_groups_equipment_id_name",
        ),
    )
    op.create_index(
        "ix_sensor_groups_equipment_id",
        "sensor_groups",
        ["equipment_id"],
        unique=False,
    )
    op.create_index(
        "ix_sensor_groups_data_source_id",
        "sensor_groups",
        ["data_source_id"],
        unique=False,
    )
    op.create_index(
        "ix_sensor_groups_group_type_is_active",
        "sensor_groups",
        ["group_type", "is_active"],
        unique=False,
    )

    op.create_table(
        "sensor_group_members",
        sa.Column("sensor_group_id", sa.Text(), nullable=False),
        sa.Column("sensor_id", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["sensor_group_id"], ["sensor_groups.sensor_group_id"]),
        sa.ForeignKeyConstraint(["sensor_id"], ["sensors.sensor_id"]),
        sa.PrimaryKeyConstraint("sensor_group_id", "sensor_id"),
    )
    op.create_index(
        "ix_sensor_group_members_sensor_id",
        "sensor_group_members",
        ["sensor_id"],
        unique=False,
    )

    op.create_table(
        "equipment_state_snapshots",
        sa.Column("snapshot_id", sa.Text(), nullable=False),
        sa.Column("equipment_id", sa.Text(), nullable=False),
        sa.Column("status", equipment_status, nullable=False),
        sa.Column("severity", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_source_id", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_sources.source_id"]),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.equipment_id"]),
        sa.PrimaryKeyConstraint("snapshot_id"),
    )
    op.create_index(
        "ix_equipment_state_snapshots_equipment_id",
        "equipment_state_snapshots",
        ["equipment_id"],
        unique=False,
    )
    op.create_index(
        "ix_equipment_state_snapshots_data_source_id",
        "equipment_state_snapshots",
        ["data_source_id"],
        unique=False,
    )
    op.execute(
        "CREATE INDEX ix_equipment_state_snapshots_equipment_effective_at_desc "
        "ON equipment_state_snapshots (equipment_id, effective_at DESC)"
    )
    op.execute(
        "CREATE INDEX ix_equipment_state_snapshots_status_effective_at_desc "
        "ON equipment_state_snapshots (status, effective_at DESC)"
    )

    op.create_table(
        "equipment_state_snapshot_sensors",
        sa.Column("snapshot_id", sa.Text(), nullable=False),
        sa.Column("sensor_id", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["sensor_id"], ["sensors.sensor_id"]),
        sa.ForeignKeyConstraint(["snapshot_id"], ["equipment_state_snapshots.snapshot_id"]),
        sa.PrimaryKeyConstraint("snapshot_id", "sensor_id"),
    )
    op.create_index(
        "ix_equipment_state_snapshot_sensors_sensor_id",
        "equipment_state_snapshot_sensors",
        ["sensor_id"],
        unique=False,
    )

    op.create_table(
        "equipment_state_snapshot_sensor_groups",
        sa.Column("snapshot_id", sa.Text(), nullable=False),
        sa.Column("sensor_group_id", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["sensor_group_id"], ["sensor_groups.sensor_group_id"]),
        sa.ForeignKeyConstraint(["snapshot_id"], ["equipment_state_snapshots.snapshot_id"]),
        sa.PrimaryKeyConstraint("snapshot_id", "sensor_group_id"),
    )
    op.create_index(
        "ix_equipment_state_snapshot_sensor_groups_sensor_group_id",
        "equipment_state_snapshot_sensor_groups",
        ["sensor_group_id"],
        unique=False,
    )

    op.create_table(
        "equipment_state_records",
        sa.Column("record_id", sa.Text(), nullable=False),
        sa.Column("equipment_id", sa.Text(), nullable=False),
        sa.Column("author_actor_id", sa.Text(), nullable=False),
        sa.Column("channel", channel, nullable=False),
        sa.Column("status", equipment_status, nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_type", data_source_type, nullable=False),
        sa.Column(
            "review_status",
            review_status,
            server_default=sa.text("'pending'::review_status"),
            nullable=False,
        ),
        sa.Column("reviewed_by_actor_id", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_comment", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.Text(), nullable=True),
        sa.Column("payload_hash", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["author_actor_id"], ["system_actors.actor_id"]),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.equipment_id"]),
        sa.ForeignKeyConstraint(["reviewed_by_actor_id"], ["system_actors.actor_id"]),
        sa.PrimaryKeyConstraint("record_id"),
    )
    op.create_index(
        "ix_equipment_state_records_equipment_id",
        "equipment_state_records",
        ["equipment_id"],
        unique=False,
    )
    op.create_index(
        "ix_equipment_state_records_author_actor_id",
        "equipment_state_records",
        ["author_actor_id"],
        unique=False,
    )
    op.create_index(
        "ix_equipment_state_records_reviewed_by_actor_id",
        "equipment_state_records",
        ["reviewed_by_actor_id"],
        unique=False,
    )
    op.execute(
        "CREATE INDEX ix_equipment_state_records_equipment_observed_at_desc "
        "ON equipment_state_records (equipment_id, observed_at DESC)"
    )
    op.execute(
        "CREATE INDEX ix_equipment_state_records_review_status_created_at_desc "
        "ON equipment_state_records (review_status, created_at DESC)"
    )
    op.create_index(
        "ix_equipment_state_records_idempotency_key_not_null",
        "equipment_state_records",
        ["idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )

    op.create_table(
        "equipment_state_record_sensors",
        sa.Column("record_id", sa.Text(), nullable=False),
        sa.Column("sensor_id", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["record_id"], ["equipment_state_records.record_id"]),
        sa.ForeignKeyConstraint(["sensor_id"], ["sensors.sensor_id"]),
        sa.PrimaryKeyConstraint("record_id", "sensor_id"),
    )
    op.create_index(
        "ix_equipment_state_record_sensors_sensor_id",
        "equipment_state_record_sensors",
        ["sensor_id"],
        unique=False,
    )

    op.create_table(
        "equipment_state_record_sensor_groups",
        sa.Column("record_id", sa.Text(), nullable=False),
        sa.Column("sensor_group_id", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["record_id"], ["equipment_state_records.record_id"]),
        sa.ForeignKeyConstraint(["sensor_group_id"], ["sensor_groups.sensor_group_id"]),
        sa.PrimaryKeyConstraint("record_id", "sensor_group_id"),
    )
    op.create_index(
        "ix_equipment_state_record_sensor_groups_sensor_group_id",
        "equipment_state_record_sensor_groups",
        ["sensor_group_id"],
        unique=False,
    )

    op.create_table(
        "knowledge_items",
        sa.Column("knowledge_item_id", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("knowledge_item_id"),
    )
    op.create_index(
        "ix_knowledge_items_is_active",
        "knowledge_items",
        ["is_active"],
        unique=False,
    )

    op.create_table(
        "knowledge_item_equipment_types",
        sa.Column("knowledge_item_id", sa.Text(), nullable=False),
        sa.Column("equipment_type", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["knowledge_item_id"], ["knowledge_items.knowledge_item_id"]),
        sa.PrimaryKeyConstraint("knowledge_item_id", "equipment_type"),
    )

    op.create_table(
        "knowledge_item_sensor_types",
        sa.Column("knowledge_item_id", sa.Text(), nullable=False),
        sa.Column("sensor_type", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["knowledge_item_id"], ["knowledge_items.knowledge_item_id"]),
        sa.PrimaryKeyConstraint("knowledge_item_id", "sensor_type"),
    )

    op.create_table(
        "knowledge_item_sensor_group_types",
        sa.Column("knowledge_item_id", sa.Text(), nullable=False),
        sa.Column("sensor_group_type", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["knowledge_item_id"], ["knowledge_items.knowledge_item_id"]),
        sa.PrimaryKeyConstraint("knowledge_item_id", "sensor_group_type"),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("knowledge_item_sensor_group_types")
    op.drop_table("knowledge_item_sensor_types")
    op.drop_table("knowledge_item_equipment_types")
    op.drop_index("ix_knowledge_items_is_active", table_name="knowledge_items")
    op.drop_table("knowledge_items")

    op.drop_index(
        "ix_equipment_state_record_sensor_groups_sensor_group_id",
        table_name="equipment_state_record_sensor_groups",
    )
    op.drop_table("equipment_state_record_sensor_groups")
    op.drop_index(
        "ix_equipment_state_record_sensors_sensor_id",
        table_name="equipment_state_record_sensors",
    )
    op.drop_table("equipment_state_record_sensors")
    op.drop_index(
        "ix_equipment_state_records_idempotency_key_not_null",
        table_name="equipment_state_records",
    )
    op.execute("DROP INDEX ix_equipment_state_records_review_status_created_at_desc")
    op.execute("DROP INDEX ix_equipment_state_records_equipment_observed_at_desc")
    op.drop_index(
        "ix_equipment_state_records_reviewed_by_actor_id",
        table_name="equipment_state_records",
    )
    op.drop_index(
        "ix_equipment_state_records_author_actor_id",
        table_name="equipment_state_records",
    )
    op.drop_index(
        "ix_equipment_state_records_equipment_id",
        table_name="equipment_state_records",
    )
    op.drop_table("equipment_state_records")

    op.drop_index(
        "ix_equipment_state_snapshot_sensor_groups_sensor_group_id",
        table_name="equipment_state_snapshot_sensor_groups",
    )
    op.drop_table("equipment_state_snapshot_sensor_groups")
    op.drop_index(
        "ix_equipment_state_snapshot_sensors_sensor_id",
        table_name="equipment_state_snapshot_sensors",
    )
    op.drop_table("equipment_state_snapshot_sensors")
    op.execute("DROP INDEX ix_equipment_state_snapshots_status_effective_at_desc")
    op.execute("DROP INDEX ix_equipment_state_snapshots_equipment_effective_at_desc")
    op.drop_index(
        "ix_equipment_state_snapshots_data_source_id",
        table_name="equipment_state_snapshots",
    )
    op.drop_index(
        "ix_equipment_state_snapshots_equipment_id",
        table_name="equipment_state_snapshots",
    )
    op.drop_table("equipment_state_snapshots")

    op.drop_index(
        "ix_sensor_group_members_sensor_id",
        table_name="sensor_group_members",
    )
    op.drop_table("sensor_group_members")

    op.drop_index(
        "ix_sensor_groups_group_type_is_active",
        table_name="sensor_groups",
    )
    op.drop_index(
        "ix_sensor_groups_data_source_id",
        table_name="sensor_groups",
    )
    op.drop_index(
        "ix_sensor_groups_equipment_id",
        table_name="sensor_groups",
    )
    op.drop_table("sensor_groups")

    op.drop_index("ix_sensors_sensor_type_is_active", table_name="sensors")
    op.drop_index("ix_sensors_data_source_id", table_name="sensors")
    op.drop_index("ix_sensors_equipment_id", table_name="sensors")
    op.drop_table("sensors")

    op.drop_index(
        "ix_equipment_equipment_code_not_null",
        table_name="equipment",
    )
    op.drop_index("ix_equipment_current_status_is_active", table_name="equipment")
    op.drop_index("ix_equipment_owner_actor_id", table_name="equipment")
    op.drop_index("ix_equipment_location_id", table_name="equipment")
    op.drop_table("equipment")

    op.drop_index("ix_data_sources_source_type", table_name="data_sources")
    op.drop_table("data_sources")

    op.drop_index(
        "ix_locations_location_type_is_active",
        table_name="locations",
    )
    op.drop_index(
        "ix_locations_parent_location_id",
        table_name="locations",
    )
    op.drop_table("locations")

    op.drop_index(
        "ix_system_actors_role_is_active",
        table_name="system_actors",
    )
    op.drop_index(
        "ix_system_actors_external_id",
        table_name="system_actors",
    )
    op.drop_table("system_actors")

    bind = op.get_bind()
    for enum_type in (
        review_status,
        data_source_type,
        channel,
        actor_role,
        equipment_status,
    ):
        enum_type.drop(bind, checkfirst=True)
