# Iteration 03: Admin Dashboard — Plan

## Goal

Build the admin dashboard page (`/admin`) that gives administrators a real-time overview of the monitored fleet.

## Scope

### KPI Cards
Four summary cards fetched from `GET /api/v1/admin/dashboard`:
- Total equipment count
- Equipment in **critical** status
- Equipment in **warning** status
- Number of clients under maintenance

### Activity Chart
Line chart (recharts `LineChart`) showing the number of maintenance actions per day over the last 14 days. Data source: `activity_chart` field of the dashboard response.

### Progress Matrix
Grid heatmap built with recharts showing equipment coverage by zone/location. Each cell reflects the completion percentage of scheduled maintenance for the corresponding area.

### Clients Table
Paginated table (shadcn `Table`) listing clients with their status summary. Data source: `GET /api/v1/admin/clients`.

### Events Feed
Live scrollable feed of the most recent state-change and action events. Data source: `GET /api/v1/admin/events`.

## Component Structure

```
src/components/admin/
  admin-dashboard.tsx   — root orchestrator, data fetch
  kpi-cards.tsx         — 4 KPI stat cards
  activity-chart.tsx    — recharts LineChart wrapper
  progress-matrix.tsx   — recharts heatmap / grid
  clients-table.tsx     — shadcn Table with pagination
  events-feed.tsx       — scrollable event list
src/app/admin/
  page.tsx              — Next.js page, renders AdminDashboard
```

## Technology

- **recharts** — ActivityChart and ProgressMatrix visualisations
- **shadcn/ui** — Card, Table, Badge, Skeleton, ScrollArea
- **Client-side data fetching** — `useEffect` + fetch inside components; no server-side secrets needed for admin API

## API Endpoints Used

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/admin/dashboard` | KPI cards, activity chart, progress matrix |
| `GET /api/v1/admin/clients` | Clients table |
| `GET /api/v1/admin/events` | Events feed |

## Out of Scope

- Authentication gate (handled by layout/middleware)
- Real-time WebSocket push (polling on page load is sufficient for iteration 3)
