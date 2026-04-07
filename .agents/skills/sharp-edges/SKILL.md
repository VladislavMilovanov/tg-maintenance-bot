---
name: sharp-edges
description: PostgreSQL sharp edges, common pitfalls, performance traps, and gotchas. Covers NULL semantics, implicit casts, transaction isolation subtleties, index misuse, JSONB performance traps, connection pooling issues, vacuum/bloat, and common migration mistakes. Use when debugging unexpected PostgreSQL behavior, reviewing queries, or hardening production database usage.
---

# PostgreSQL Sharp Edges

PostgreSQL is powerful, but it has sharp edges that bite even experienced developers. This skill catalogs the most common gotchas, counterintuitive behaviors, and performance traps — with concrete mitigations.

## When to Use This Skill

- Debugging unexpected query results or missing rows
- Reviewing queries that should be fast but aren't
- Auditing schema migrations for safety
- Diagnosing bloat, lock contention, or connection exhaustion in production
- Writing application code that interacts with PostgreSQL correctly
- Designing schemas that won't cause surprises later

---

## NULL Semantics

### NULL is Not Equal to Anything — Including Itself

```sql
-- These return NULL, not TRUE or FALSE
SELECT NULL = NULL;   -- NULL
SELECT NULL != NULL;  -- NULL
SELECT NULL = 1;      -- NULL

-- This is the ONLY way to check for NULL
SELECT NULL IS NULL;  -- TRUE
SELECT NULL IS NOT NULL; -- FALSE

-- Dangerous: NULL rows are silently excluded
SELECT * FROM users WHERE deleted_at != '2024-01-01'; -- rows where deleted_at IS NULL are excluded!

-- Correct:
SELECT * FROM users WHERE deleted_at IS NULL OR deleted_at != '2024-01-01';
```

### NOT IN with NULLs Returns No Rows

```sql
-- If ANY value in the subquery is NULL, NOT IN returns empty set
SELECT * FROM orders WHERE user_id NOT IN (SELECT id FROM banned_users);
-- If banned_users has a single NULL id → returns 0 rows!

-- Safe alternative: NOT EXISTS
SELECT * FROM orders o
WHERE NOT EXISTS (SELECT 1 FROM banned_users b WHERE b.id = o.user_id);

-- Or: ensure the subquery has no NULLs
SELECT * FROM orders WHERE user_id NOT IN (
  SELECT id FROM banned_users WHERE id IS NOT NULL
);
```

### NULL in Aggregates

```sql
-- COUNT(*) vs COUNT(col): COUNT(col) ignores NULLs
SELECT COUNT(*), COUNT(email) FROM users;
-- COUNT(*): total rows
-- COUNT(email): rows where email IS NOT NULL

-- SUM/AVG of all NULLs returns NULL, not 0
SELECT AVG(score) FROM results WHERE category = 'nonexistent'; -- NULL

-- Use COALESCE to handle:
SELECT COALESCE(AVG(score), 0) FROM results WHERE category = 'nonexistent';
```

---

## Type Coercion and Implicit Casts

### String Literals Cast to Wrong Types

```sql
-- This works but prevents index use on timestamptz columns
SELECT * FROM events WHERE created_at > '2024-01-01';
-- PostgreSQL casts '2024-01-01' to date, then to timestamptz using local timezone!

-- Be explicit:
SELECT * FROM events WHERE created_at > '2024-01-01 00:00:00+00'::timestamptz;
-- Or with parameter binding: use a proper timestamptz from your application
```

### Operator Does Not Exist — UUID vs Text

```sql
-- Common error: comparing uuid column with text value
SELECT * FROM users WHERE id = '550e8400-e29b-41d4-a716-446655440000'; -- OK, auto-cast
SELECT * FROM users WHERE id = ANY('{550e8400...}'::text[]); -- ERROR: operator does not exist

-- Fix: cast explicitly
SELECT * FROM users WHERE id = ANY('{550e8400...}'::uuid[]);
```

### Integer Division Truncates

```sql
SELECT 7 / 2;       -- 3, not 3.5!
SELECT 7.0 / 2;     -- 3.5
SELECT 7::numeric / 2;  -- 3.5

-- In application code, always cast when computing ratios:
SELECT completed::numeric / total * 100 AS pct FROM stats;
```

### Timestamp Without Time Zone is a Trap

```sql
-- timestamp stores the literal clock time with NO timezone info
-- stored value changes meaning depending on server timezone setting
ALTER TABLE events ADD created_at timestamp; -- DANGEROUS in production

-- Always use timestamptz:
ALTER TABLE events ADD created_at timestamptz NOT NULL DEFAULT now();
```

---

## Index Pitfalls

### Functions on Indexed Columns Disable Index Use

```sql
-- Index on email exists, but this does a seq scan:
SELECT * FROM users WHERE lower(email) = 'john@example.com';

-- Fix option 1: functional index
CREATE INDEX users_lower_email_idx ON users (lower(email));

-- Fix option 2: store the normalized value
-- Fix option 3: use citext extension
CREATE EXTENSION citext;
ALTER TABLE users ALTER COLUMN email TYPE citext;
```

### LIKE with Leading Wildcard Disables B-tree Index

```sql
-- Index not used:
SELECT * FROM products WHERE name LIKE '%widget%';

-- Use pg_trgm for substring search:
CREATE EXTENSION pg_trgm;
CREATE INDEX products_name_trgm_idx ON products USING gin(name gin_trgm_ops);
-- Now LIKE '%widget%' and ILIKE are index-supported
```

### Partial Index is Not Used When Condition Doesn't Match

```sql
CREATE INDEX active_users_idx ON users (email) WHERE status = 'active';

-- Only used when query contains: WHERE status = 'active'
SELECT * FROM users WHERE email = 'a@b.com' AND status = 'active'; -- uses index
SELECT * FROM users WHERE email = 'a@b.com'; -- seq scan, condition not present
```

### Index Bloat from Dead Tuples

```sql
-- After heavy UPDATE/DELETE workloads, indexes retain dead tuple pointers
-- Check index bloat:
SELECT
  schemaname, tablename, indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;

-- Rebuild bloated indexes online:
REINDEX INDEX CONCURRENTLY bloated_index;
```

---

## Transaction Isolation Gotchas

### Read Committed Allows Non-Repeatable Reads

```sql
-- Default isolation level: READ COMMITTED
-- Two SELECTs in the same transaction can see different data!

BEGIN;
SELECT balance FROM accounts WHERE id = 1; -- sees 1000
-- another transaction commits: UPDATE accounts SET balance = 500 WHERE id = 1
SELECT balance FROM accounts WHERE id = 1; -- sees 500 within same txn!
COMMIT;

-- Use REPEATABLE READ or SERIALIZABLE when consistency matters:
BEGIN ISOLATION LEVEL REPEATABLE READ;
```

### SELECT FOR UPDATE — Lock What You Actually Read

```sql
-- Classic lost update problem:
BEGIN;
SELECT quantity FROM inventory WHERE sku = 'WIDGET'; -- reads 5
-- another transaction reads 5, both decide to decrement
UPDATE inventory SET quantity = quantity - 1 WHERE sku = 'WIDGET'; -- race!
COMMIT;

-- Fix: SELECT FOR UPDATE acquires row lock
BEGIN;
SELECT quantity FROM inventory WHERE sku = 'WIDGET' FOR UPDATE;
-- now other transactions wait here until we commit
UPDATE inventory SET quantity = quantity - 1 WHERE sku = 'WIDGET';
COMMIT;
```

### Serialization Failures Must Be Retried

```sql
-- With SERIALIZABLE isolation, transactions may fail with:
-- ERROR: could not serialize access due to concurrent update (40001)
-- Your application MUST retry these transactions.

-- Python example:
from psycopg2 import errors
for attempt in range(5):
    try:
        with conn.cursor() as cur:
            cur.execute("BEGIN ISOLATION LEVEL SERIALIZABLE")
            # ... do work
            conn.commit()
            break
    except errors.SerializationFailure:
        conn.rollback()
        if attempt == 4:
            raise
```

### DDL Acquires AccessExclusiveLock

```sql
-- These block ALL reads and writes while running:
ALTER TABLE orders ADD COLUMN notes text;        -- full table lock
ALTER TABLE orders ALTER COLUMN amount TYPE numeric(12,2); -- rewrites table!
CREATE INDEX orders_user_id_idx ON orders(user_id); -- blocks writes

-- Safe alternatives:
-- Add nullable column with no default (instant):
ALTER TABLE orders ADD COLUMN notes text;

-- Add column with default (PostgreSQL 11+ is instant for non-volatile defaults):
ALTER TABLE orders ADD COLUMN archived boolean NOT NULL DEFAULT false;

-- Build index without blocking:
CREATE INDEX CONCURRENTLY orders_user_id_idx ON orders(user_id);
```

---

## JSONB Performance Traps

### Querying JSONB Without an Index is a Full Table Scan

```sql
-- Without index, this scans every row:
SELECT * FROM events WHERE payload->>'type' = 'purchase';

-- Add a GIN index:
CREATE INDEX events_payload_gin ON events USING gin(payload);

-- Or targeted expression index for known keys:
CREATE INDEX events_type_idx ON events ((payload->>'type'));
```

### JSONB Operator Precedence Surprises

```sql
-- Chained -> returns jsonb, ->> returns text
SELECT payload->'user'->>'id' FROM events;  -- OK: get user.id as text
SELECT payload->>'user'->'id' FROM events;  -- ERROR: text has no -> operator

-- Extracting nested paths cleanly:
SELECT payload #>> '{user,address,city}' FROM events; -- path operator
```

### Updating a Single JSONB Key is Inefficient

```sql
-- This reads the entire jsonb, modifies, rewrites entire column:
UPDATE events SET payload = payload || '{"processed": true}';

-- For high-churn individual keys, consider a dedicated column instead.
-- jsonb_set is no better — still full column rewrite:
UPDATE events SET payload = jsonb_set(payload, '{processed}', 'true');
```

### JSONB vs HSTORE vs Relational

- Use **relational columns** when you know the structure and query it frequently
- Use **JSONB** for optional/irregular attributes or when the schema evolves rapidly
- Use **HSTORE** only for legacy compatibility; JSONB is strictly better

---

## Connection Pooling Issues

### PostgreSQL Process-Per-Connection Architecture

Each connection spawns an OS process (~5–10MB RAM). At 500 connections:
- ~2.5–5GB RAM just for connection overhead
- Context switching degrades performance
- **Always use a connection pooler** in production (PgBouncer, pgpool-II, or Supabase pooler)

### PgBouncer Transaction Mode Breaks Session-Level Features

```sql
-- PgBouncer transaction mode (recommended for most apps) breaks:
-- SET LOCAL, session variables, advisory locks, LISTEN/NOTIFY, prepared statements

-- Don't use in transaction-mode pooling:
SET search_path TO my_schema;          -- lost after transaction
SELECT pg_advisory_lock(1234);         -- released unpredictably
PREPARE my_stmt AS SELECT ...;        -- not available in next transaction

-- Session mode pooling allows these but loses the connection count benefit
```

### Connection Exhaustion Under Load

```sql
-- Monitor connections:
SELECT count(*), state, wait_event_type, wait_event
FROM pg_stat_activity
GROUP BY state, wait_event_type, wait_event
ORDER BY count DESC;

-- Set pool_size in application (asyncpg example):
pool = await asyncpg.create_pool(dsn, min_size=5, max_size=20)
-- Total connections = max_size * app_instances; keep < max_connections - 10
```

---

## VACUUM and Table Bloat

### Dead Tuples and Table Bloat

PostgreSQL uses MVCC — UPDATE and DELETE leave dead tuples. Without regular vacuuming:
- Table files grow indefinitely (bloat)
- Index scans slow down (dead tuples in indexes)
- Transaction ID wraparound (catastrophic, database shuts down!)

```sql
-- Check table bloat:
SELECT
  relname,
  n_dead_tup,
  n_live_tup,
  round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 1) AS dead_pct,
  last_autovacuum,
  last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- Force vacuum on a specific table (non-blocking):
VACUUM (VERBOSE, ANALYZE) orders;

-- Reclaim space (locks table briefly — use only on tables with extreme bloat):
VACUUM FULL orders;  -- prefer pg_repack for zero-downtime alternative
```

### autovacuum Tuning for High-Churn Tables

```sql
-- Default autovacuum triggers at 20% dead tuple ratio — too conservative for large tables
-- For a 100M row table, default threshold = 20M dead tuples before vacuum triggers!

ALTER TABLE orders SET (
  autovacuum_vacuum_scale_factor = 0.01,   -- vacuum at 1% dead tuples
  autovacuum_vacuum_threshold = 1000,       -- minimum 1000 dead tuples
  autovacuum_analyze_scale_factor = 0.005
);
```

---

## Common Migration Mistakes

### Adding NOT NULL Column with Default to Large Table

```sql
-- PostgreSQL < 11: rewrites entire table — avoid on large tables in production
ALTER TABLE orders ADD COLUMN archived boolean NOT NULL DEFAULT false;

-- Safe approach for PostgreSQL < 11 (multi-step):
ALTER TABLE orders ADD COLUMN archived boolean;          -- instant, nullable
UPDATE orders SET archived = false WHERE archived IS NULL; -- batch in app
ALTER TABLE orders ALTER COLUMN archived SET NOT NULL;    -- fast scan
ALTER TABLE orders ALTER COLUMN archived SET DEFAULT false;

-- PostgreSQL 11+: adding NOT NULL with a constant default is instant (no rewrite)
```

### Renaming Columns Breaks Running Application Code

```sql
-- Old and new code run simultaneously during zero-downtime deploys
-- Renaming column breaks old code immediately

-- Safe rename pattern:
-- 1. Add new column (nullable)
ALTER TABLE users ADD COLUMN full_name text;
-- 2. Backfill (can be batched)
UPDATE users SET full_name = name WHERE full_name IS NULL;
-- 3. Deploy app that writes BOTH columns
-- 4. Add NOT NULL constraint once backfill is complete
ALTER TABLE users ALTER COLUMN full_name SET NOT NULL;
-- 5. Deploy app that reads only new column
-- 6. Drop old column
ALTER TABLE users DROP COLUMN name;
```

### Long Transactions Block Autovacuum

```sql
-- A long-running transaction (or idle transaction!) prevents autovacuum
-- from cleaning rows newer than that transaction's snapshot.
-- This causes table bloat to accumulate rapidly.

-- Find long-running or idle transactions:
SELECT pid, now() - xact_start AS duration, state, query
FROM pg_stat_activity
WHERE state != 'idle'
  AND xact_start IS NOT NULL
ORDER BY duration DESC;

-- Set statement and transaction timeouts:
-- In postgresql.conf:
-- idle_in_transaction_session_timeout = '5min'
-- statement_timeout = '30s'
```

---

## Best Practices Summary

1. **Always use `timestamptz`**, never `timestamp without time zone`
2. **Use `IS NULL` / `IS NOT NULL`**, never `= NULL`
3. **Prefer `NOT EXISTS` over `NOT IN`** when the subquery can contain NULLs
4. **Create indexes `CONCURRENTLY`** in production to avoid write locks
5. **Use a connection pooler** (PgBouncer) — never connect directly from app servers at scale
6. **Monitor `n_dead_tup`** and tune autovacuum for high-write tables
7. **Avoid long-running transactions** — set `idle_in_transaction_session_timeout`
8. **Test migrations on a production-size copy** before running in production
9. **Explicit casts over implicit ones** — prevents plan instability and subtle bugs
10. **Use `EXPLAIN (ANALYZE, BUFFERS)`** to understand actual query plans, not just estimated ones
