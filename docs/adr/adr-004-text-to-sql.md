# ADR-004: Text-to-SQL for Natural Language Database Queries

## Status

Accepted

## Context

Users — engineers, operators, and admins — need to retrieve analytical insights from the equipment maintenance database without writing SQL or navigating complex dashboard filters. Typical questions include:

- "How many equipment units are in critical status?"
- "Show top-3 problematic equipment over the last 7 days"
- "What percentage of equipment is in normal condition?"
- "Show all locations and the count of equipment at each"

The existing assistant chat flow (`POST /api/v1/assistant/messages`) handles conversational queries backed by an LLM (via OpenRouter), but it lacks direct access to live aggregated database data. Without a structured query layer, answers to data-driven questions are either hallucinated or unavailable.

## Decision

Implement an LLM-based Text-to-SQL pipeline as a new backend endpoint `POST /api/v1/query/text-to-sql`, with read-only safety guardrails.

### Flow

```
User question (natural language)
        │
        ▼
[1] LLM generates SQL
    • System prompt includes full DB schema (tables, columns, types)
    • Model is instructed to output only a SELECT statement
        │
        ▼
[2] SQL validation (safety layer)
    • Only SELECT statements allowed
    • Blocklist check: INSERT, UPDATE, DELETE, DROP, ALTER,
      TRUNCATE, CREATE, GRANT, REVOKE
    • Reject immediately if any mutation keyword found
        │
        ▼
[3] Execute against read-only DB connection
    • sqlalchemy.text() with async session
    • Statement timeout: 5 seconds
    • Row limit: 100 rows max
        │
        ▼
[4] LLM summarizes results in natural language
    • Receives question + SQL + tabular results
    • Returns a concise human-readable answer
        │
        ▼
[5] API response: answer + sql_query + row data
```

### Safety Guardrails

| Guardrail | Implementation |
|---|---|
| Only SELECT allowed | Parse first non-whitespace keyword; reject if not SELECT |
| Mutation blocklist | Regex check for INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, GRANT, REVOKE |
| Query timeout | `SET LOCAL statement_timeout = '5000'` before execution |
| Row limit | `LIMIT 100` enforced at application layer (added to SQL if absent) |
| Read-only connection | Separate DB session used only for SELECT execution |

### Authentication

The endpoint requires `Authorization: Bearer {token}` (same scheme as other protected endpoints).

## Alternatives Considered

### RAG over DB (Retrieval-Augmented Generation)

Build vector embeddings over database records and retrieve relevant chunks before answering. **Rejected** because structured relational data is best queried via SQL, not similarity search. Aggregations, counts, and joins are not expressible as semantic similarity.

### Hardcoded Query Templates

Predefine a library of parameterized SQL templates and map user intent to templates via classification. **Rejected** because it cannot cover the open-ended variety of analytical questions and requires manual maintenance of the template library as the schema evolves.

### Hybrid Approach (Template + LLM fallback)

Use templates for common queries, fall back to LLM for others. **Rejected** as unnecessary complexity for MVP. LLM-based Text-to-SQL already covers the common cases with acceptable quality, and adding template routing increases maintenance burden without clear benefit at this stage.

## Consequences

**Positive:**
- Users can ask arbitrary data questions in natural language
- No custom query UI or filter configuration needed
- Reuses existing OpenRouter/LLM infrastructure
- Results are transparent — SQL query is returned alongside the answer

**Negative:**
- LLM-generated SQL may be incorrect for complex questions (acceptable degradation: error is returned to user)
- LLM call adds latency (two LLM calls: SQL generation + summarization)
- Requires embedding full schema in every prompt (token cost)

**Mitigations:**
- Clear error messages guide users to rephrase
- Prompt engineering minimizes hallucinated SQL
- Schema prompt uses only essential table/column info (no indexes)
