---
name: postgresql-table-design
description: Review and design PostgreSQL schemas with emphasis on data types, constraints, indexes, normalization, migrations, and query-oriented performance.
---

# PostgreSQL Table Design

Use this skill when designing new tables, reviewing an existing schema, or checking whether a PostgreSQL data model fits the workload.

## Focus Areas

- Pick PostgreSQL-native types intentionally: `timestamptz`, `text`, `numeric`, `jsonb`, `uuid`, arrays, ranges.
- Prefer `generated always as identity` over legacy `serial`.
- Require explicit primary keys unless the table is true append-only event/log storage.
- Add `not null`, `check`, `unique`, and foreign keys where they express real invariants.
- Remember that PostgreSQL does not auto-index foreign keys.
- Normalize first; denormalize only for measured read-path wins.
- Treat `jsonb` as an escape hatch for optional or irregular attributes, not as a default relational substitute.

## Review Checklist

1. Verify every table has a clear ownership and lifecycle model.
2. Check whether column types match actual semantics, not just current sample values.
3. Confirm nullable columns are genuinely optional.
4. Validate foreign key actions: `restrict`, `cascade`, `set null`, `set default`.
5. Add indexes for real filters, joins, sorts, and uniqueness guarantees.
6. Check audit fields like `created_at`, `updated_at`, `deleted_at` for consistency.
7. Review naming: `snake_case`, singular/plural consistency, no quoted identifiers.
8. Consider migration safety for large tables and production rollouts.

## Practical Guidance

### Data Types

- IDs: prefer `bigint generated always as identity`; use `uuid` when distributed generation or opaque identifiers matter.
- Money: use `numeric(p, s)`, never floating point.
- Text: default to `text`; only add length checks when the business rule actually needs them.
- Time: prefer `timestamptz`; avoid `timestamp without time zone`.
- Status-like fields: use lookup tables or constrained text; use enums only for small, stable sets.
- Semi-structured data: use `jsonb` with targeted indexes if query patterns justify it.

### Constraints

- Use `not null` aggressively for required data.
- Add `check` constraints for ranges, finite state subsets, and structural assumptions.
- Prefer database-enforced uniqueness over app-level assumptions.
- Use composite uniqueness when the invariant spans multiple columns.

### Indexing

- Create indexes for:
  - foreign keys
  - frequent filters
  - join keys
  - sort paths used in production queries
  - unique business identifiers
- Prefer composite indexes that match actual `where` + `order by` patterns.
- Use partial indexes for hot subsets like active rows.
- Use `gin` for `jsonb`, arrays, and full-text cases where appropriate.

## Output Expectations

When asked to review a schema:

- Identify integrity risks first.
- Call out missing constraints and missing indexes separately.
- Note PostgreSQL-specific improvements, not generic SQL advice.
- Suggest concrete DDL snippets when the fix is unambiguous.
- Mention migration risk when changes may rewrite or lock large tables.

## Example Recommendations

```sql
create table maintenance_tasks (
  id bigint generated always as identity primary key,
  equipment_id bigint not null references equipment(id) on delete restrict,
  status text not null check (status in ('pending', 'in_progress', 'done')),
  title text not null,
  due_at timestamptz,
  created_at timestamptz not null default now()
);

create index maintenance_tasks_equipment_id_idx on maintenance_tasks (equipment_id);
create index maintenance_tasks_status_due_at_idx on maintenance_tasks (status, due_at);
```

Use this skill to challenge weak schema decisions early, before they become migration debt.
