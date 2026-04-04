"""Import sample progress data into the local PostgreSQL database."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert

from maintenance_backend.config import Settings, load_local_env
from maintenance_backend.db_schema import TABLES_BY_NAME
from maintenance_backend.db_urls import to_sqlalchemy_sync_url


IMPORT_FILE = Path("data/progress-import.v1.json")
IMPORT_VERSION = "progress-import.v1"
IMPORT_ORDER = (
    "system_actors",
    "locations",
    "data_sources",
    "equipment",
    "sensors",
    "sensor_groups",
    "sensor_group_members",
    "equipment_state_snapshots",
    "equipment_state_snapshot_sensors",
    "equipment_state_snapshot_sensor_groups",
    "equipment_state_records",
    "equipment_state_record_sensors",
    "equipment_state_record_sensor_groups",
    "knowledge_items",
    "knowledge_item_equipment_types",
    "knowledge_item_sensor_types",
    "knowledge_item_sensor_group_types",
)


def _normalize_value(column_name: str, value: Any) -> Any:
    if isinstance(value, str) and column_name.endswith("_at"):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: _normalize_value(key, value) for key, value in row.items()}


def _load_payload() -> dict[str, Any]:
    if not IMPORT_FILE.exists():
        msg = f"Import file not found: {IMPORT_FILE}"
        raise FileNotFoundError(msg)
    payload = json.loads(IMPORT_FILE.read_text(encoding="utf-8"))
    if payload.get("schema_version") != IMPORT_VERSION:
        msg = (
            f"Unsupported import schema_version: {payload.get('schema_version')!r}. "
            f"Expected {IMPORT_VERSION!r}."
        )
        raise ValueError(msg)
    return payload


def _upsert_rows(connection: Any, table_name: str, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    table = TABLES_BY_NAME[table_name]
    pk_columns = [column.name for column in table.primary_key.columns]
    for raw_row in rows:
        normalized_row = _normalize_row(raw_row)
        base_insert = insert(table).values(normalized_row)
        update_columns = {
            column_name: getattr(base_insert.excluded, column_name)
            for column_name in normalized_row
            if column_name not in pk_columns
        }

        if update_columns:
            statement = base_insert.on_conflict_do_update(
                index_elements=pk_columns,
                set_=update_columns,
            )
        else:
            statement = base_insert.on_conflict_do_nothing(index_elements=pk_columns)

        connection.execute(statement)
    return len(rows)


def main() -> None:
    """Import the versioned sample dataset into PostgreSQL."""

    load_local_env()
    settings = Settings()
    payload = _load_payload()

    engine = create_engine(to_sqlalchemy_sync_url(settings.database_url), future=True)
    inserted_counts: dict[str, int] = {}
    with engine.begin() as connection:
        for table_name in IMPORT_ORDER:
            inserted_counts[table_name] = _upsert_rows(
                connection,
                table_name,
                payload.get(table_name, []),
            )

    print("Imported sample dataset from data/progress-import.v1.json")
    for table_name in IMPORT_ORDER:
        count = inserted_counts[table_name]
        if count:
            print(f"- {table_name}: {count}")


if __name__ == "__main__":
    main()
