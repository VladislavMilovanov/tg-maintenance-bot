"""Inspect the migrated/imported local PostgreSQL dataset."""

from __future__ import annotations

from sqlalchemy import create_engine, text

from maintenance_backend.config import Settings, load_local_env
from maintenance_backend.db_urls import to_sqlalchemy_sync_url


COUNT_QUERIES = (
    ("system_actors", "SELECT COUNT(*) FROM system_actors"),
    ("locations", "SELECT COUNT(*) FROM locations"),
    ("equipment", "SELECT COUNT(*) FROM equipment"),
    ("data_sources", "SELECT COUNT(*) FROM data_sources"),
    ("sensors", "SELECT COUNT(*) FROM sensors"),
    ("sensor_groups", "SELECT COUNT(*) FROM sensor_groups"),
    ("equipment_state_snapshots", "SELECT COUNT(*) FROM equipment_state_snapshots"),
    ("equipment_state_records", "SELECT COUNT(*) FROM equipment_state_records"),
    ("knowledge_items", "SELECT COUNT(*) FROM knowledge_items"),
)

DETAIL_QUERY = """
SELECT
    e.equipment_id,
    e.name AS equipment_name,
    l.name AS location_name,
    e.current_status,
    r.record_id,
    r.status AS record_status,
    r.observed_at,
    a.display_name AS author_name
FROM equipment AS e
JOIN locations AS l ON l.location_id = e.location_id
LEFT JOIN equipment_state_records AS r ON r.equipment_id = e.equipment_id
LEFT JOIN system_actors AS a ON a.actor_id = r.author_actor_id
ORDER BY e.equipment_id, r.observed_at DESC NULLS LAST
LIMIT 10
"""


def main() -> None:
    """Print a short summary of the current DB state."""

    load_local_env()
    settings = Settings()
    engine = create_engine(to_sqlalchemy_sync_url(settings.database_url), future=True)

    with engine.connect() as connection:
        print("Table counts:")
        for label, query in COUNT_QUERIES:
            value = connection.execute(text(query)).scalar_one()
            print(f"- {label}: {value}")

        print("\nEquipment + latest records:")
        rows = connection.execute(text(DETAIL_QUERY)).mappings().all()
        if not rows:
            print("- no rows")
            return
        for row in rows:
            print(
                f"- {row['equipment_id']} | {row['equipment_name']} | "
                f"location={row['location_name']} | current_status={row['current_status']} | "
                f"record={row['record_id']} | record_status={row['record_status']} | "
                f"observed_at={row['observed_at']} | author={row['author_name']}"
            )


if __name__ == "__main__":
    main()
