# Iteration 04: Main Dashboard — Plan

## Goal

Build the 3 core user-facing screens with drill-down navigation:
`/dashboard` → `/dashboard/equipment/[equipment_id]` → `/dashboard/equipment/[equipment_id]/nodes/[sensor_group_id]`

## Screen 1: Plant Overview Dashboard (`/dashboard`)

**Route:** `frontend/src/app/(main)/dashboard/page.tsx` — server component wrapper that renders `<PlantDashboard>`.

**Components (`src/components/dashboard/`):**
- `plant-dashboard.tsx` — orchestrator, fetches plant overview data on mount
- `plant-status-badge.tsx` — green/yellow/red badge with label
- `status-summary.tsx` — 4 counters (normal / warning / critical / unknown)
- `daily-status-chart.tsx` — 14-day bar chart of worst daily status (recharts)
- `worst-performers.tsx` — list of top problematic equipment with links to drill-down
- `state-feed.tsx` — live feed of equipment state changes
- `action-feed.tsx` — live feed of maintenance actions

**Layout:** status badge + summary → chart → 2-column grid (worst performers | state feed) → action feed.

**API calls:** `GET /api/v1/dashboard/plant-overview`, `GET /api/v1/dashboard/state-feed`, `GET /api/v1/dashboard/action-feed`.

---

## Screen 2: Equipment Detail (`/dashboard/equipment/[equipment_id]`)

**Route:** `frontend/src/app/(main)/dashboard/equipment/[equipment_id]/page.tsx` — extracts param and renders `<EquipmentDetail>`.

**Components:**
- `equipment-detail.tsx` — orchestrator, tabs, data fetch
- `equipment-header.tsx` — name, code, location, status badge
- `maintenance-progress.tsx` — progress bar for maintenance completion
- `top-nodes.tsx` — top sensor groups with status badges and navigation links
- `equipment-history.tsx` — paginated state + action history table

**Tabs:** "Общие данные" (general info table) | "Ключевые узлы" (top nodes list).

**API calls:** `GET /api/v1/equipment/{id}`, `GET /api/v1/equipment/{id}/history`.

---

## Screen 3: Sensor Group Detail (`/dashboard/equipment/[equipment_id]/nodes/[sensor_group_id]`)

**Route:** `frontend/src/app/(main)/dashboard/equipment/[equipment_id]/nodes/[sensor_group_id]/page.tsx` — extracts both params and renders `<SensorGroupDetail>`.

**Components:**
- `sensor-group-detail.tsx` — orchestrator, data fetch
- `sensor-group-header.tsx` — name, status badge, breadcrumb links
- `node-image.tsx` — equipment image with fallback placeholder
- `sensor-list.tsx` — table of sensor readings with status indicators
- `ai-diagnosis.tsx` — fires `sendAssistantMessage()` on mount with equipment context; shows streaming/loading state

**API calls:** `GET /api/v1/sensor-groups/{id}`, `POST /api/v1/assistant/messages` (AI diagnosis).

---

## Key Decisions

- Drill-down URLs use nested dynamic routes (`[equipment_id]`, `[sensor_group_id]`).
- Equipment page uses client-side tab toggle (not URL routing).
- AI diagnosis fires on mount with a `useEffect`; loading skeleton shown until response arrives.
- Breadcrumbs on screens 2 and 3 provide hierarchy context for navigation.
- All data-fetching components are `"use client"` with cancellation via `cancelled` flag to avoid state updates on unmounted components.
