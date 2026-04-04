"""Runtime ORM models for the backend persistence layer."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, relationship

from maintenance_backend.db_schema import (
    equipment,
    equipment_state_records,
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


class Equipment(Base):
    """Runtime ORM model for persisted equipment."""

    __table__ = equipment

    state_records = relationship(
        "EquipmentStateRecord",
        foreign_keys=lambda: [EquipmentStateRecord.equipment_id],
        back_populates="equipment",
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
