"""Runtime ORM models for the backend persistence layer."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, relationship

from maintenance_backend.db_schema import (
    data_sources,
    equipment,
    equipment_state_records,
    equipment_state_snapshots,
    locations,
    sensor_groups,
    sensors,
    system_actors,
)


class Base(DeclarativeBase):
    """Declarative base for runtime SQLAlchemy models."""


class SystemActor(Base):
    """Runtime ORM model for persisted system actors."""

    __table__ = system_actors

    authored_records = relationship(
        "EquipmentStateRecord",
        foreign_keys=lambda: [EquipmentStateRecord.author_actor_id],
        back_populates="author",
    )


class Location(Base):
    """Runtime ORM model for persisted locations."""

    __table__ = locations

    children = relationship(
        "Location",
        foreign_keys=[locations.c.parent_location_id],
        back_populates="parent",
        lazy="select",
    )
    parent = relationship(
        "Location",
        foreign_keys=[locations.c.parent_location_id],
        back_populates="children",
        remote_side=[locations.c.location_id],
    )


class Equipment(Base):
    """Runtime ORM model for persisted equipment."""

    __table__ = equipment

    location = relationship(
        "Location",
        foreign_keys=[equipment.c.location_id],
    )
    state_records = relationship(
        "EquipmentStateRecord",
        foreign_keys=lambda: [EquipmentStateRecord.equipment_id],
        back_populates="equipment",
    )


class Sensor(Base):
    """Runtime ORM model for persisted sensors."""

    __table__ = sensors

    equipment = relationship(
        "Equipment",
        foreign_keys=[sensors.c.equipment_id],
    )


class SensorGroup(Base):
    """Runtime ORM model for persisted sensor groups."""

    __table__ = sensor_groups

    equipment = relationship(
        "Equipment",
        foreign_keys=[sensor_groups.c.equipment_id],
    )


class DataSource(Base):
    """Runtime ORM model for persisted data sources."""

    __table__ = data_sources


class EquipmentStateSnapshot(Base):
    """Runtime ORM model for persisted equipment state snapshots."""

    __table__ = equipment_state_snapshots

    equipment = relationship(
        "Equipment",
        foreign_keys=[equipment_state_snapshots.c.equipment_id],
    )


class EquipmentStateRecord(Base):
    """Runtime ORM model for persisted equipment state records."""

    __table__ = equipment_state_records

    equipment = relationship(
        "Equipment",
        foreign_keys=[equipment_state_records.c.equipment_id],
        back_populates="state_records",
    )
    author = relationship(
        "SystemActor",
        foreign_keys=[equipment_state_records.c.author_actor_id],
        back_populates="authored_records",
    )
