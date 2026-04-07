# Iteration 03: Admin Dashboard — Summary

## What Was Done

### Dependencies installed
- `recharts` — chart library for ActivityChart and ProgressMatrix
- shadcn components added: `card`, `table`, `badge`, `skeleton`, `scroll-area`

### Components built (7 total)

| File | Description |
|---|---|
| `src/components/admin/admin-dashboard.tsx` | Root orchestrator; fetches `GET /api/v1/admin/dashboard` client-side, renders all sub-components with Skeleton loading states |
| `src/components/admin/kpi-cards.tsx` | Four KPI stat cards (total equipment, critical, warning, clients) using shadcn Card |
| `src/components/admin/activity-chart.tsx` | recharts `LineChart` showing daily maintenance actions over 14 days |
| `src/components/admin/progress-matrix.tsx` | recharts-based grid/heatmap showing maintenance coverage per equipment zone |
| `src/components/admin/clients-table.tsx` | shadcn `Table` listing clients fetched from `GET /api/v1/admin/clients` |
| `src/components/admin/events-feed.tsx` | Scrollable event list fetched from `GET /api/v1/admin/events` with status badges |
| `src/app/admin/page.tsx` | Next.js App Router page; replaced placeholder, renders `<AdminDashboard />` |

### Lint fix applied
The initial implementation called `setLoading(true)` and `setError(null)` synchronously inside `useEffect`, which triggered the `react-hooks/set-state-in-effect` ESLint rule. Fixed by initialising state to the correct values in `useState` and using a `cancelled` flag pattern to guard async callbacks.

## Verification Results

### `pnpm build`
```
✓ Compiled successfully in 2.8s
✓ Finished TypeScript in 2.1s
✓ Generating static pages (8/8)

Route (app)
  ○ /admin   — static
```
**Result: PASS**

### `pnpm lint`
```
(no output — zero errors, zero warnings)
```
**Result: PASS**

### `uv run pytest backend/tests/ -v --tb=short`
```
60 passed in 0.72s
```
**Result: PASS — no regressions**
