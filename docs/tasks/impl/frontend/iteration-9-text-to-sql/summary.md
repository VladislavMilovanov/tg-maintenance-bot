# Iteration 9: Text-to-SQL — Summary

## Status: Done ✅

## What Was Built

### ADR: `docs/adr/adr-004-text-to-sql.md`

Architecture Decision Record documenting the choice of LLM-based Text-to-SQL over RAG and hardcoded templates. Key points:

- **Decision:** `POST /api/v1/query/text-to-sql` with a 4-step LLM pipeline
- **Rejected:** RAG over DB (semantic similarity can't express aggregations), hardcoded templates (brittle, can't cover open-ended questions), hybrid approach (unnecessary complexity)
- **Mitigations:** Explicit safety guardrails, SQL returned to user for transparency, graceful error messages

### Backend: `TextToSqlService` (4-step pipeline)

File: `backend/src/maintenance_backend/services/text_to_sql.py`

| Step | Description |
|---|---|
| 1 | LLM generates SQL — system prompt embeds full DB schema, model outputs raw SELECT |
| 2 | `validate_sql()` safety check — first-keyword check + mutation blocklist regex |
| 3 | Execute via `sqlalchemy.text()` with async session, 5 s timeout, LIMIT 100 |
| 4 | LLM summarises tabular results in natural language (answer language matches question) |

**Key components:**

- `TextToSqlService.answer_question(question, user_role)` — orchestrates the full pipeline
- `validate_sql(sql) -> str` — raises `ValueError` if non-SELECT or mutation keyword detected
- `OpenRouterTextToSqlGateway` — concrete LLM adapter (OpenRouter/OpenAI-compatible)
- `TextToSqlGateway` — Protocol for test doubles
- `TextToSqlGatewayError` — LLM failure exception
- `_MUTATION_KEYWORDS` — compiled regex: `INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE`
- Row limit: 100 rows max; statement timeout: 5 000 ms

### Backend: `POST /api/v1/query/text-to-sql`

File: `backend/src/maintenance_backend/api/v1/text_to_sql.py`

```
POST /api/v1/query/text-to-sql
Authorization: Bearer {token}

Request:  { "question": "Сколько единиц оборудования в статусе critical?" }
Response: {
  "answer":     "В базе 5 единиц оборудования в статусе critical.",
  "sql_query":  "SELECT COUNT(*) AS count FROM equipment WHERE current_status = 'critical'",
  "row_count":  1,
  "columns":    ["count"],
  "rows":       [[5]],
  "error":      null
}
```

### Frontend: Types and API function

**`frontend/src/lib/api/types.ts`** — two interfaces added:

```typescript
export interface TextToSqlRequest { question: string; }
export interface TextToSqlResponse {
  answer: string;
  sql_query?: string;
  row_count: number;
  columns: string[];
  rows: unknown[][];
  error?: string;
}
```

**`frontend/src/lib/api/endpoints.ts`** — one function added:

```typescript
export async function queryTextToSql(data: TextToSqlRequest): Promise<TextToSqlResponse>
```

### Documentation Updates

- **`docs/adr/adr-004-text-to-sql.md`** — full ADR (new file)
- **`docs/integrations.md`** — Text-to-SQL section with flow description and usage examples
- **`backend/docs/api-contracts.md`** — `POST /api/v1/query/text-to-sql` contract added

## Tests

**File:** `backend/tests/test_text_to_sql_api.py` — **15 new tests**

| # | Test | Type |
|---|---|---|
| 1 | Count critical equipment → row_count=1, columns=["count"] | API scenario |
| 2 | Top-3 problematic equipment last 7 days → 3 rows | API scenario |
| 3 | Percentage normal equipment → pct_normal column | API scenario |
| 4 | Locations with equipment count → location_name, equipment_count | API scenario |
| 5 | Mutation query (DELETE) → error returned, row_count=0 | API scenario |
| 6 | validate_sql accepts valid SELECT | Unit |
| 7 | validate_sql strips trailing semicolon | Unit |
| 8 | validate_sql rejects DELETE | Unit |
| 9 | validate_sql rejects INSERT | Unit |
| 10 | validate_sql rejects mutation inside SELECT (injection attempt) | Unit |
| 11 | validate_sql rejects UPDATE | Unit |
| 12 | validate_sql rejects DROP | Unit |
| 13 | No auth → 401 | Auth guard |
| 14 | Invalid token → 401 | Auth guard |
| 15 | Empty question → 422 | Validation |

**Total backend tests: 75 passed** (PYTHONPATH=backend/src uv run pytest backend/tests/ -x -q)

## Verification Results

| Check | Result |
|---|---|
| `pnpm build` | ✅ Compiled successfully, all 8 routes prerendered |
| `pnpm lint` (ESLint) | ✅ No errors |
| `npx tsc --noEmit` | ✅ No TypeScript errors |
| `pytest backend/tests/` | ✅ 75 passed in 2.17 s |
| `pytest tests/` (bot) | ✅ 5 passed in 1.49 s |

## Files Created / Modified

| File | Change |
|---|---|
| `docs/adr/adr-004-text-to-sql.md` | Created |
| `backend/src/maintenance_backend/services/text_to_sql.py` | Created |
| `backend/src/maintenance_backend/api/v1/text_to_sql.py` | Created |
| `backend/src/maintenance_backend/schemas/text_to_sql.py` | Created |
| `backend/tests/test_text_to_sql_api.py` | Created |
| `frontend/src/lib/api/types.ts` | Updated (2 interfaces added) |
| `frontend/src/lib/api/endpoints.ts` | Updated (1 function added) |
| `docs/integrations.md` | Updated |
| `backend/docs/api-contracts.md` | Updated |
| `docs/tasks/impl/frontend/iteration-9-text-to-sql/plan.md` | Created |
| `docs/tasks/impl/frontend/iteration-9-text-to-sql/summary.md` | Created (this file) |
