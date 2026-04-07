"""Read-only persistence adapters for all 13 new frontend endpoints."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import sqlalchemy as sa

from maintenance_backend.database import PostgresDatabase
from maintenance_backend.db_schema import (
    equipment,
    equipment_state_records,
    equipment_state_snapshot_sensor_groups,
    equipment_state_snapshots,
    locations,
    sensor_group_members,
    sensor_groups,
    sensors,
    system_actors,
)

# ---------------------------------------------------------------------------
# Status priority helpers
# ---------------------------------------------------------------------------

STATUS_PRIORITY: dict[str, int] = {
    "critical": 3,
    "warning": 2,
    "normal": 1,
    "unknown": 0,
}
PRIORITY_TO_STATUS: dict[int, str] = {v: k for k, v in STATUS_PRIORITY.items()}


def _status_priority_case(col: sa.ColumnElement) -> sa.Case:
    """Return a CASE expression mapping status string to numeric priority."""
    return sa.case(
        (col == "critical", 3),
        (col == "warning", 2),
        (col == "normal", 1),
        else_=0,
    )


def _priority_to_status(priority: int | None) -> str:
    if priority is None:
        return "unknown"
    return PRIORITY_TO_STATUS.get(priority, "unknown")


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------


class PostgresReadRepository:
    """Read-only query repository for all frontend API endpoints."""

    def __init__(self, database: PostgresDatabase) -> None:
        self._db = database

    # ------------------------------------------------------------------
    # 1. Plant overview
    # ------------------------------------------------------------------

    async def get_plant_overview(self) -> dict:
        async with self._db.session() as session:
            # status_summary: count active equipment by status
            summary_q = (
                sa.select(
                    equipment.c.current_status,
                    sa.func.count().label("cnt"),
                )
                .where(equipment.c.is_active == sa.true())
                .group_by(equipment.c.current_status)
            )
            summary_rows = (await session.execute(summary_q)).fetchall()

            status_summary: dict[str, int] = {
                "normal": 0,
                "warning": 0,
                "critical": 0,
                "unknown": 0,
            }
            for row in summary_rows:
                s = row.current_status
                if s in status_summary:
                    status_summary[s] = row.cnt
                else:
                    status_summary["unknown"] += row.cnt

            # plant_status: worst across all active equipment
            worst_priority_q = sa.select(
                sa.func.max(_status_priority_case(equipment.c.current_status)).label(
                    "worst"
                )
            ).where(equipment.c.is_active == sa.true())
            worst_priority = (await session.execute(worst_priority_q)).scalar()
            plant_status = _priority_to_status(worst_priority)

            # daily_history: snapshots per day × status for last 14 days
            cutoff = datetime.now(tz=UTC) - timedelta(days=14)
            daily_q = (
                sa.select(
                    sa.func.date(equipment_state_snapshots.c.observed_at).label("day"),
                    equipment_state_snapshots.c.status,
                    sa.func.count().label("cnt"),
                )
                .where(equipment_state_snapshots.c.observed_at >= cutoff)
                .group_by(
                    sa.func.date(equipment_state_snapshots.c.observed_at),
                    equipment_state_snapshots.c.status,
                )
                .order_by(sa.func.date(equipment_state_snapshots.c.observed_at))
            )
            daily_rows = (await session.execute(daily_q)).fetchall()

            daily_map: dict[str, dict[str, int]] = {}
            for row in daily_rows:
                day_str = str(row.day)
                if day_str not in daily_map:
                    daily_map[day_str] = {
                        "normal": 0,
                        "warning": 0,
                        "critical": 0,
                        "unknown": 0,
                    }
                s = row.status
                if s in daily_map[day_str]:
                    daily_map[day_str][s] = row.cnt
                else:
                    daily_map[day_str]["unknown"] += row.cnt

            daily_history = [
                {"date": day, **counts} for day, counts in sorted(daily_map.items())
            ]

            # worst_performers: top 5 critical/warning equipment
            latest_snap_sq = (
                sa.select(
                    equipment_state_snapshots.c.equipment_id,
                    sa.func.max(equipment_state_snapshots.c.observed_at).label(
                        "last_observed"
                    ),
                )
                .group_by(equipment_state_snapshots.c.equipment_id)
                .subquery()
            )

            performers_q = (
                sa.select(
                    equipment.c.equipment_id,
                    equipment.c.name,
                    equipment.c.current_status,
                    locations.c.name.label("location_name"),
                    latest_snap_sq.c.last_observed,
                )
                .join(locations, equipment.c.location_id == locations.c.location_id)
                .outerjoin(
                    latest_snap_sq,
                    equipment.c.equipment_id == latest_snap_sq.c.equipment_id,
                )
                .where(
                    equipment.c.is_active == sa.true(),
                    equipment.c.current_status.in_(["critical", "warning"]),
                )
                .order_by(
                    _status_priority_case(equipment.c.current_status).desc(),
                    latest_snap_sq.c.last_observed.desc().nullslast(),
                )
                .limit(5)
            )
            performers_rows = (await session.execute(performers_q)).fetchall()

            # Fetch latest comment for each worst performer
            performer_ids = [r.equipment_id for r in performers_rows]
            latest_comment_map: dict[str, str | None] = {}
            if performer_ids:
                latest_comment_sq = (
                    sa.select(
                        equipment_state_records.c.equipment_id,
                        sa.func.max(equipment_state_records.c.observed_at).label(
                            "latest_observed"
                        ),
                    )
                    .where(equipment_state_records.c.equipment_id.in_(performer_ids))
                    .group_by(equipment_state_records.c.equipment_id)
                    .subquery()
                )
                comments_q = (
                    sa.select(
                        equipment_state_records.c.equipment_id,
                        equipment_state_records.c.comment,
                    )
                    .join(
                        latest_comment_sq,
                        sa.and_(
                            equipment_state_records.c.equipment_id
                            == latest_comment_sq.c.equipment_id,
                            equipment_state_records.c.observed_at
                            == latest_comment_sq.c.latest_observed,
                        ),
                    )
                    .where(equipment_state_records.c.equipment_id.in_(performer_ids))
                )
                comment_rows = (await session.execute(comments_q)).fetchall()
                for cr in comment_rows:
                    latest_comment_map[cr.equipment_id] = cr.comment

            now = datetime.now(tz=UTC)
            worst_performers = [
                {
                    "equipment_id": r.equipment_id,
                    "name": r.name,
                    "current_status": r.current_status,
                    "location_name": r.location_name,
                    "last_changed_at": r.last_observed,
                    "duration_in_status_hours": (
                        int((now - r.last_observed).total_seconds() / 3600)
                        if r.last_observed is not None
                        else None
                    ),
                    "last_comment": latest_comment_map.get(r.equipment_id),
                }
                for r in performers_rows
            ]

            # Compute trend from daily_history
            sorted_days = sorted(daily_map.keys())
            if len(sorted_days) >= 2:
                newest = daily_map[sorted_days[-1]]
                # Compare against 7 days ago if available, else first entry
                ref_idx = max(0, len(sorted_days) - 8)
                oldest = daily_map[sorted_days[ref_idx]]
            elif len(sorted_days) == 1:
                newest = daily_map[sorted_days[0]]
                oldest = {"critical": 0, "warning": 0}
            else:
                newest = {"critical": 0, "warning": 0}
                oldest = {"critical": 0, "warning": 0}

            critical_delta = newest.get("critical", 0) - oldest.get("critical", 0)
            warning_delta = newest.get("warning", 0) - oldest.get("warning", 0)
            combined_delta = critical_delta + warning_delta
            if combined_delta < 0:
                direction = "improved"
            elif combined_delta > 0:
                direction = "worsened"
            else:
                direction = "stable"

        return {
            "plant_status": plant_status,
            "status_summary": status_summary,
            "daily_history": daily_history,
            "worst_performers": worst_performers,
            "trend": {
                "critical_delta": critical_delta,
                "warning_delta": warning_delta,
                "direction": direction,
            },
        }

    # ------------------------------------------------------------------
    # 2. State feed
    # ------------------------------------------------------------------

    async def get_state_feed(self, limit: int = 20, offset: int = 0) -> dict:
        async with self._db.session() as session:
            base = (
                sa.select(
                    equipment_state_snapshots.c.snapshot_id,
                    equipment_state_snapshots.c.equipment_id,
                    equipment.c.name.label("equipment_name"),
                    equipment_state_snapshots.c.status.label("new_status"),
                    equipment_state_snapshots.c.observed_at.label("changed_at"),
                )
                .join(
                    equipment,
                    equipment_state_snapshots.c.equipment_id
                    == equipment.c.equipment_id,
                )
                .order_by(equipment_state_snapshots.c.observed_at.desc())
            )

            total_q = sa.select(sa.func.count()).select_from(
                equipment_state_snapshots.join(
                    equipment,
                    equipment_state_snapshots.c.equipment_id
                    == equipment.c.equipment_id,
                )
            )
            total = (await session.execute(total_q)).scalar() or 0

            rows = (await session.execute(base.limit(limit).offset(offset))).fetchall()
            items = [
                {
                    "equipment_id": r.equipment_id,
                    "equipment_name": r.equipment_name,
                    "old_status": None,
                    "new_status": r.new_status,
                    "changed_at": r.changed_at,
                }
                for r in rows
            ]

        return {"items": items, "total": total}

    # ------------------------------------------------------------------
    # 3. Action feed
    # ------------------------------------------------------------------

    async def get_action_feed(self, limit: int = 20, offset: int = 0) -> dict:
        async with self._db.session() as session:
            base = (
                sa.select(
                    equipment_state_records.c.record_id,
                    equipment_state_records.c.equipment_id,
                    equipment.c.name.label("equipment_name"),
                    equipment_state_records.c.status,
                    equipment_state_records.c.comment,
                    equipment_state_records.c.observed_at,
                    equipment_state_records.c.channel,
                    system_actors.c.display_name.label("author_name"),
                )
                .join(
                    equipment,
                    equipment_state_records.c.equipment_id == equipment.c.equipment_id,
                )
                .join(
                    system_actors,
                    equipment_state_records.c.author_actor_id
                    == system_actors.c.actor_id,
                )
                .order_by(equipment_state_records.c.created_at.desc())
            )

            total_q = sa.select(sa.func.count()).select_from(
                equipment_state_records.join(
                    equipment,
                    equipment_state_records.c.equipment_id == equipment.c.equipment_id,
                ).join(
                    system_actors,
                    equipment_state_records.c.author_actor_id
                    == system_actors.c.actor_id,
                )
            )
            total = (await session.execute(total_q)).scalar() or 0

            rows = (await session.execute(base.limit(limit).offset(offset))).fetchall()
            items = [
                {
                    "record_id": r.record_id,
                    "equipment_id": r.equipment_id,
                    "equipment_name": r.equipment_name,
                    "status": r.status,
                    "comment": r.comment,
                    "observed_at": r.observed_at,
                    "channel": r.channel,
                    "author_name": r.author_name,
                }
                for r in rows
            ]

        return {"items": items, "total": total}

    # ------------------------------------------------------------------
    # 4. List equipment
    # ------------------------------------------------------------------

    async def list_equipment(
        self,
        location_id: str | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        owner_actors = system_actors.alias("owner_actors")

        async with self._db.session() as session:
            base = (
                sa.select(
                    equipment.c.equipment_id,
                    equipment.c.name,
                    equipment.c.equipment_code,
                    equipment.c.current_status,
                    equipment.c.location_id,
                    locations.c.name.label("location_name"),
                    owner_actors.c.actor_id.label("owner_actor_id_val"),
                    owner_actors.c.display_name.label("owner_display_name"),
                )
                .join(locations, equipment.c.location_id == locations.c.location_id)
                .outerjoin(
                    owner_actors, equipment.c.owner_actor_id == owner_actors.c.actor_id
                )
                .where(equipment.c.is_active == sa.true())
            )

            count_from = equipment.join(
                locations, equipment.c.location_id == locations.c.location_id
            )
            count_filters = [equipment.c.is_active == sa.true()]

            if location_id is not None:
                base = base.where(equipment.c.location_id == location_id)
                count_filters.append(equipment.c.location_id == location_id)
            if status is not None:
                base = base.where(equipment.c.current_status == status)
                count_filters.append(equipment.c.current_status == status)

            base = base.order_by(equipment.c.name.asc())

            count_q = (
                sa.select(sa.func.count()).select_from(count_from).where(*count_filters)
            )
            total = (await session.execute(count_q)).scalar() or 0

            rows = (await session.execute(base.limit(limit).offset(offset))).fetchall()
            items = [
                {
                    "equipment_id": r.equipment_id,
                    "name": r.name,
                    "equipment_code": r.equipment_code,
                    "current_status": r.current_status,
                    "location": {
                        "location_id": r.location_id,
                        "name": r.location_name,
                    },
                    "owner": (
                        {
                            "actor_id": r.owner_actor_id_val,
                            "display_name": r.owner_display_name,
                        }
                        if r.owner_actor_id_val is not None
                        else None
                    ),
                }
                for r in rows
            ]

        return {"items": items, "total": total}

    # ------------------------------------------------------------------
    # 5. Equipment detail
    # ------------------------------------------------------------------

    async def get_equipment_detail(self, equipment_id: str) -> dict | None:
        owner_actors = system_actors.alias("owner_actors")

        async with self._db.session() as session:
            eq_q = (
                sa.select(
                    equipment.c.equipment_id,
                    equipment.c.name,
                    equipment.c.equipment_code,
                    equipment.c.current_status,
                    equipment.c.location_id,
                    locations.c.name.label("location_name"),
                    owner_actors.c.actor_id.label("owner_actor_id_val"),
                    owner_actors.c.display_name.label("owner_display_name"),
                    equipment.c.maintenance_due_at,
                    equipment.c.maintenance_completed_at,
                )
                .join(locations, equipment.c.location_id == locations.c.location_id)
                .outerjoin(
                    owner_actors, equipment.c.owner_actor_id == owner_actors.c.actor_id
                )
                .where(equipment.c.equipment_id == equipment_id)
            )
            eq_row = (await session.execute(eq_q)).fetchone()
            if eq_row is None:
                return None

            # maintenance_progress: fraction of time elapsed between completed → due
            maintenance_progress: float | None = None
            due = eq_row.maintenance_due_at
            completed = eq_row.maintenance_completed_at
            if due is not None and completed is not None:
                total_span = (due - completed).total_seconds()
                if total_span > 0:
                    elapsed = (datetime.now(tz=UTC) - completed).total_seconds()
                    maintenance_progress = min(max(elapsed / total_span, 0.0), 1.0)

            # sensor_groups_count
            sg_count_q = (
                sa.select(sa.func.count())
                .select_from(sensor_groups)
                .where(
                    sensor_groups.c.equipment_id == equipment_id,
                    sensor_groups.c.is_active == sa.true(),
                )
            )
            sensor_groups_count = (await session.execute(sg_count_q)).scalar() or 0

            # last_state_change
            last_change_q = sa.select(
                sa.func.max(equipment_state_snapshots.c.observed_at)
            ).where(equipment_state_snapshots.c.equipment_id == equipment_id)
            last_state_change = (await session.execute(last_change_q)).scalar()

            # top_nodes: sensor groups with worst status from latest snapshot per group
            latest_snap_per_group_sq = (
                sa.select(
                    equipment_state_snapshot_sensor_groups.c.sensor_group_id,
                    sa.func.max(equipment_state_snapshots.c.observed_at).label(
                        "latest_observed"
                    ),
                )
                .join(
                    equipment_state_snapshots,
                    equipment_state_snapshot_sensor_groups.c.snapshot_id
                    == equipment_state_snapshots.c.snapshot_id,
                )
                .where(equipment_state_snapshots.c.equipment_id == equipment_id)
                .group_by(equipment_state_snapshot_sensor_groups.c.sensor_group_id)
                .subquery()
            )

            snap_status_sq = (
                sa.select(
                    equipment_state_snapshot_sensor_groups.c.sensor_group_id,
                    equipment_state_snapshots.c.status.label("group_status"),
                )
                .join(
                    equipment_state_snapshots,
                    equipment_state_snapshot_sensor_groups.c.snapshot_id
                    == equipment_state_snapshots.c.snapshot_id,
                )
                .join(
                    latest_snap_per_group_sq,
                    sa.and_(
                        equipment_state_snapshot_sensor_groups.c.sensor_group_id
                        == latest_snap_per_group_sq.c.sensor_group_id,
                        equipment_state_snapshots.c.observed_at
                        == latest_snap_per_group_sq.c.latest_observed,
                    ),
                )
                .subquery()
            )

            sensor_count_sq = (
                sa.select(
                    sensor_group_members.c.sensor_group_id,
                    sa.func.count().label("sensor_count"),
                )
                .group_by(sensor_group_members.c.sensor_group_id)
                .subquery()
            )

            top_nodes_q = (
                sa.select(
                    sensor_groups.c.sensor_group_id,
                    sensor_groups.c.name,
                    sensor_groups.c.group_type,
                    snap_status_sq.c.group_status,
                    sa.func.coalesce(sensor_count_sq.c.sensor_count, 0).label(
                        "sensor_count"
                    ),
                )
                .outerjoin(
                    snap_status_sq,
                    sensor_groups.c.sensor_group_id == snap_status_sq.c.sensor_group_id,
                )
                .outerjoin(
                    sensor_count_sq,
                    sensor_groups.c.sensor_group_id
                    == sensor_count_sq.c.sensor_group_id,
                )
                .where(
                    sensor_groups.c.equipment_id == equipment_id,
                    sensor_groups.c.is_active == sa.true(),
                )
                .order_by(
                    _status_priority_case(
                        sa.func.coalesce(
                            snap_status_sq.c.group_status,
                            sa.cast(
                                sa.literal("unknown"), equipment.c.current_status.type
                            ),
                        )
                    ).desc()
                )
                .limit(3)
            )
            top_nodes_rows = (await session.execute(top_nodes_q)).fetchall()

            top_nodes = [
                {
                    "sensor_group_id": r.sensor_group_id,
                    "name": r.name,
                    "group_type": r.group_type,
                    "status": r.group_status
                    if r.group_status is not None
                    else "unknown",
                    "sensor_count": r.sensor_count,
                }
                for r in top_nodes_rows
            ]

        return {
            "equipment_id": eq_row.equipment_id,
            "name": eq_row.name,
            "equipment_code": eq_row.equipment_code,
            "current_status": eq_row.current_status,
            "location": {
                "location_id": eq_row.location_id,
                "name": eq_row.location_name,
            },
            "owner": (
                {
                    "actor_id": eq_row.owner_actor_id_val,
                    "display_name": eq_row.owner_display_name,
                }
                if eq_row.owner_actor_id_val is not None
                else None
            ),
            "maintenance_progress": maintenance_progress,
            "top_nodes": top_nodes,
            "sensor_groups_count": sensor_groups_count,
            "last_state_change": last_state_change,
            "duration_in_status_hours": (
                int((datetime.now(tz=UTC) - last_state_change).total_seconds() / 3600)
                if last_state_change is not None
                else None
            ),
        }

    # ------------------------------------------------------------------
    # 6. Equipment history
    # ------------------------------------------------------------------

    async def get_equipment_history(
        self,
        equipment_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        async with self._db.session() as session:
            base = (
                sa.select(
                    equipment_state_records.c.record_id,
                    equipment_state_records.c.status,
                    equipment_state_records.c.comment,
                    equipment_state_records.c.observed_at,
                    equipment_state_records.c.created_at,
                    equipment_state_records.c.channel,
                    system_actors.c.external_id.label("author_external_id"),
                    system_actors.c.display_name.label("author_display_name"),
                    system_actors.c.role.label("author_role"),
                )
                .join(
                    system_actors,
                    equipment_state_records.c.author_actor_id
                    == system_actors.c.actor_id,
                )
                .where(equipment_state_records.c.equipment_id == equipment_id)
                .order_by(equipment_state_records.c.observed_at.desc())
            )

            total_q = (
                sa.select(sa.func.count())
                .select_from(equipment_state_records)
                .where(equipment_state_records.c.equipment_id == equipment_id)
            )
            total = (await session.execute(total_q)).scalar() or 0

            rows = (await session.execute(base.limit(limit).offset(offset))).fetchall()
            items = [
                {
                    "record_id": r.record_id,
                    "status": r.status,
                    "comment": r.comment,
                    "observed_at": r.observed_at,
                    "created_at": r.created_at,
                    "channel": r.channel,
                    "author": {
                        "external_id": r.author_external_id,
                        "display_name": r.author_display_name,
                        "role": r.author_role,
                    },
                }
                for r in rows
            ]

        return {"items": items, "total": total}

    # ------------------------------------------------------------------
    # 7. Sensor group detail
    # ------------------------------------------------------------------

    async def get_sensor_group_detail(self, sensor_group_id: str) -> dict | None:
        async with self._db.session() as session:
            sg_q = (
                sa.select(
                    sensor_groups.c.sensor_group_id,
                    sensor_groups.c.name,
                    sensor_groups.c.group_type,
                    sensor_groups.c.image_url,
                    sensor_groups.c.equipment_id,
                    equipment.c.name.label("equipment_name"),
                )
                .join(
                    equipment, sensor_groups.c.equipment_id == equipment.c.equipment_id
                )
                .where(sensor_groups.c.sensor_group_id == sensor_group_id)
            )
            sg_row = (await session.execute(sg_q)).fetchone()
            if sg_row is None:
                return None

            # Group status from latest snapshot referencing this group
            latest_snap_q = (
                sa.select(equipment_state_snapshots.c.status)
                .join(
                    equipment_state_snapshot_sensor_groups,
                    equipment_state_snapshot_sensor_groups.c.snapshot_id
                    == equipment_state_snapshots.c.snapshot_id,
                )
                .where(
                    equipment_state_snapshot_sensor_groups.c.sensor_group_id
                    == sensor_group_id
                )
                .order_by(equipment_state_snapshots.c.observed_at.desc())
                .limit(1)
            )
            group_status_val = (await session.execute(latest_snap_q)).scalar()
            group_status = (
                group_status_val if group_status_val is not None else "unknown"
            )

            # Sensors in this group
            sensors_q = (
                sa.select(
                    sensors.c.sensor_id,
                    sensors.c.name,
                    sensors.c.sensor_type,
                    sensors.c.last_observed_at,
                )
                .join(
                    sensor_group_members,
                    sensor_group_members.c.sensor_id == sensors.c.sensor_id,
                )
                .where(sensor_group_members.c.sensor_group_id == sensor_group_id)
                .order_by(sensors.c.name)
            )
            sensor_rows = (await session.execute(sensors_q)).fetchall()
            sensors_list = [
                {
                    "sensor_id": r.sensor_id,
                    "name": r.name,
                    "sensor_type": r.sensor_type,
                    "last_observed_at": r.last_observed_at,
                }
                for r in sensor_rows
            ]

        return {
            "sensor_group_id": sg_row.sensor_group_id,
            "name": sg_row.name,
            "status": group_status,
            "group_type": sg_row.group_type,
            "image_url": sg_row.image_url,
            "equipment": {
                "equipment_id": sg_row.equipment_id,
                "name": sg_row.equipment_name,
            },
            "sensors": sensors_list,
        }

    # ------------------------------------------------------------------
    # 8. Location tree
    # ------------------------------------------------------------------

    async def get_location_tree(self) -> list[dict]:
        async with self._db.session() as session:
            locs_q = (
                sa.select(
                    locations.c.location_id,
                    locations.c.name,
                    locations.c.location_type,
                    locations.c.parent_location_id,
                )
                .where(locations.c.is_active == sa.true())
                .order_by(locations.c.display_order)
            )
            locs_rows = (await session.execute(locs_q)).fetchall()

            if not locs_rows:
                return []

            # Equipment count and worst status per location (direct equipment only)
            eq_stats_q = (
                sa.select(
                    equipment.c.location_id,
                    sa.func.count().label("eq_count"),
                    sa.func.max(
                        _status_priority_case(equipment.c.current_status)
                    ).label("worst_priority"),
                )
                .where(equipment.c.is_active == sa.true())
                .group_by(equipment.c.location_id)
            )
            eq_stats_rows = (await session.execute(eq_stats_q)).fetchall()
            eq_stats: dict[str, dict] = {
                r.location_id: {
                    "count": r.eq_count,
                    "worst_priority": r.worst_priority
                    if r.worst_priority is not None
                    else 0,
                }
                for r in eq_stats_rows
            }

            # Build node map
            loc_map: dict[str, dict] = {}
            for r in locs_rows:
                loc_map[r.location_id] = {
                    "location_id": r.location_id,
                    "name": r.name,
                    "location_type": r.location_type,
                    "_parent_id": r.parent_location_id,
                    "equipment_count": eq_stats.get(r.location_id, {}).get("count", 0),
                    "_direct_worst": eq_stats.get(r.location_id, {}).get(
                        "worst_priority", 0
                    ),
                    "status": "unknown",
                    "children": [],
                }

            # Wire up parent → children
            roots: list[dict] = []
            for loc in loc_map.values():
                parent_id = loc["_parent_id"]
                if parent_id is None or parent_id not in loc_map:
                    roots.append(loc)
                else:
                    loc_map[parent_id]["children"].append(loc)

            # Bottom-up status aggregation
            def _aggregate(node: dict) -> int:
                worst = node["_direct_worst"]
                for child in node["children"]:
                    child_worst = _aggregate(child)
                    if child_worst > worst:
                        worst = child_worst
                node["status"] = _priority_to_status(worst)
                return worst

            for root in roots:
                _aggregate(root)

            # Strip internal keys
            def _clean(node: dict) -> dict:
                node.pop("_direct_worst", None)
                node.pop("_parent_id", None)
                node["children"] = [_clean(c) for c in node["children"]]
                return node

            return [_clean(r) for r in roots]

    # ------------------------------------------------------------------
    # 9. Admin dashboard
    # ------------------------------------------------------------------

    async def get_admin_dashboard(self) -> dict:
        async with self._db.session() as session:
            # KPIs
            total_eq_q = (
                sa.select(sa.func.count())
                .select_from(equipment)
                .where(equipment.c.is_active == sa.true())
            )
            total_equipment = (await session.execute(total_eq_q)).scalar() or 0

            critical_q = (
                sa.select(sa.func.count())
                .select_from(equipment)
                .where(
                    equipment.c.is_active == sa.true(),
                    equipment.c.current_status == "critical",
                )
            )
            critical_count = (await session.execute(critical_q)).scalar() or 0

            warning_q = (
                sa.select(sa.func.count())
                .select_from(equipment)
                .where(
                    equipment.c.is_active == sa.true(),
                    equipment.c.current_status == "warning",
                )
            )
            warning_count = (await session.execute(warning_q)).scalar() or 0

            clients_q = sa.select(
                sa.func.count(sa.distinct(system_actors.c.actor_id))
            ).where(
                system_actors.c.is_active == sa.true(),
                system_actors.c.role.in_(["user", "operator", "engineer"]),
            )
            clients_count = (await session.execute(clients_q)).scalar() or 0

            # Activity chart: records per day for last 14 days
            cutoff = datetime.now(tz=UTC) - timedelta(days=14)
            activity_q = (
                sa.select(
                    sa.func.date(equipment_state_records.c.created_at).label("day"),
                    sa.func.count().label("cnt"),
                )
                .where(equipment_state_records.c.created_at >= cutoff)
                .group_by(sa.func.date(equipment_state_records.c.created_at))
                .order_by(sa.func.date(equipment_state_records.c.created_at))
            )
            activity_rows = (await session.execute(activity_q)).fetchall()
            activity_chart = [
                {"date": str(r.day), "actions_count": r.cnt} for r in activity_rows
            ]

            # Progress matrix: per location, count equipment by status
            matrix_q = (
                sa.select(
                    locations.c.name.label("location_name"),
                    equipment.c.current_status,
                    sa.func.count().label("cnt"),
                )
                .join(locations, equipment.c.location_id == locations.c.location_id)
                .where(equipment.c.is_active == sa.true())
                .group_by(locations.c.name, equipment.c.current_status)
                .order_by(locations.c.name)
            )
            matrix_rows = (await session.execute(matrix_q)).fetchall()

            matrix_map: dict[str, dict] = {}
            for r in matrix_rows:
                if r.location_name not in matrix_map:
                    matrix_map[r.location_name] = {
                        "location_name": r.location_name,
                        "total": 0,
                        "normal": 0,
                        "warning": 0,
                        "critical": 0,
                    }
                matrix_map[r.location_name]["total"] += r.cnt
                if r.current_status in ("normal", "warning", "critical"):
                    matrix_map[r.location_name][r.current_status] += r.cnt

            progress_matrix = list(matrix_map.values())

        return {
            "kpis": {
                "total_equipment": total_equipment,
                "critical_count": critical_count,
                "warning_count": warning_count,
                "clients_count": clients_count,
            },
            "activity_chart": activity_chart,
            "progress_matrix": progress_matrix,
        }

    # ------------------------------------------------------------------
    # 10. List clients
    # ------------------------------------------------------------------

    async def list_clients(self, limit: int = 20, offset: int = 0) -> dict:
        async with self._db.session() as session:
            # Equipment count owned by each actor
            owned_eq_sq = (
                sa.select(
                    equipment.c.owner_actor_id,
                    sa.func.count().label("eq_count"),
                )
                .where(equipment.c.is_active == sa.true())
                .group_by(equipment.c.owner_actor_id)
                .subquery()
            )

            # Latest record created_at per actor (last_activity_at)
            last_activity_sq = (
                sa.select(
                    equipment_state_records.c.author_actor_id,
                    sa.func.max(equipment_state_records.c.created_at).label("last_at"),
                )
                .group_by(equipment_state_records.c.author_actor_id)
                .subquery()
            )

            base = (
                sa.select(
                    system_actors.c.actor_id,
                    system_actors.c.external_id,
                    system_actors.c.display_name,
                    system_actors.c.role,
                    sa.func.coalesce(owned_eq_sq.c.eq_count, 0).label(
                        "equipment_count"
                    ),
                    last_activity_sq.c.last_at.label("last_activity_at"),
                )
                .outerjoin(
                    owned_eq_sq,
                    system_actors.c.actor_id == owned_eq_sq.c.owner_actor_id,
                )
                .outerjoin(
                    last_activity_sq,
                    system_actors.c.actor_id == last_activity_sq.c.author_actor_id,
                )
                .order_by(system_actors.c.display_name.asc().nullslast())
            )

            total_q = sa.select(sa.func.count()).select_from(system_actors)
            total = (await session.execute(total_q)).scalar() or 0

            rows = (await session.execute(base.limit(limit).offset(offset))).fetchall()
            items = [
                {
                    "actor_id": r.actor_id,
                    "external_id": r.external_id,
                    "display_name": r.display_name,
                    "role": r.role,
                    "equipment_count": r.equipment_count,
                    "last_activity_at": r.last_activity_at,
                }
                for r in rows
            ]

        return {"items": items, "total": total}

    # ------------------------------------------------------------------
    # 11. List events (UNION of snapshots + records)
    # ------------------------------------------------------------------

    async def list_events(self, limit: int = 20, offset: int = 0) -> dict:
        async with self._db.session() as session:
            eq_snap = equipment.alias("eq_snap")
            eq_rec = equipment.alias("eq_rec")

            snapshots_sel = sa.select(
                sa.literal("state_change").label("event_type"),
                equipment_state_snapshots.c.equipment_id,
                eq_snap.c.name.label("equipment_name"),
                sa.cast(sa.null(), sa.Text()).label("actor_name"),
                sa.func.coalesce(
                    equipment_state_snapshots.c.summary,
                    sa.cast(equipment_state_snapshots.c.status, sa.Text()),
                ).label("description"),
                equipment_state_snapshots.c.observed_at.label("occurred_at"),
            ).join(
                eq_snap,
                equipment_state_snapshots.c.equipment_id == eq_snap.c.equipment_id,
            )

            records_sel = (
                sa.select(
                    sa.literal("action").label("event_type"),
                    equipment_state_records.c.equipment_id,
                    eq_rec.c.name.label("equipment_name"),
                    system_actors.c.display_name.label("actor_name"),
                    sa.func.coalesce(
                        equipment_state_records.c.comment,
                        sa.cast(equipment_state_records.c.status, sa.Text()),
                    ).label("description"),
                    equipment_state_records.c.observed_at.label("occurred_at"),
                )
                .join(
                    eq_rec,
                    equipment_state_records.c.equipment_id == eq_rec.c.equipment_id,
                )
                .join(
                    system_actors,
                    equipment_state_records.c.author_actor_id
                    == system_actors.c.actor_id,
                )
            )

            union_sq = sa.union_all(snapshots_sel, records_sel).subquery()

            total_q = sa.select(sa.func.count()).select_from(union_sq)
            total = (await session.execute(total_q)).scalar() or 0

            events_q = (
                sa.select(union_sq)
                .order_by(union_sq.c.occurred_at.desc())
                .limit(limit)
                .offset(offset)
            )
            rows = (await session.execute(events_q)).fetchall()

            items = [
                {
                    "event_type": r.event_type,
                    "equipment_id": r.equipment_id,
                    "equipment_name": r.equipment_name,
                    "actor_name": r.actor_name,
                    "description": r.description,
                    "occurred_at": r.occurred_at,
                }
                for r in rows
            ]

        return {"items": items, "total": total}
