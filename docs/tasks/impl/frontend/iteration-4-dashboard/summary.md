# Iteration 04: Main Dashboard — Summary

## What Was Built

18 components across 3 screens implementing the full drill-down dashboard.

### Routes Created

| Route | File |
|-------|------|
| `/dashboard` | `src/app/(main)/dashboard/page.tsx` |
| `/dashboard/equipment/[equipment_id]` | `src/app/(main)/dashboard/equipment/[equipment_id]/page.tsx` |
| `/dashboard/equipment/[equipment_id]/nodes/[sensor_group_id]` | `src/app/(main)/dashboard/equipment/[equipment_id]/nodes/[sensor_group_id]/page.tsx` |

### Components (`src/components/dashboard/`)

**Screen 1 — Plant Overview (7 components):**
- `plant-dashboard.tsx` — root orchestrator with loading/error states
- `plant-status-badge.tsx` — coloured badge (normal/warning/critical/unknown)
- `status-summary.tsx` — 4-tile status count cards
- `daily-status-chart.tsx` — 14-day bar chart (recharts)
- `worst-performers.tsx` — ranked list of problematic equipment with drill-down links
- `state-feed.tsx` — paginated feed of equipment state changes
- `action-feed.tsx` — paginated feed of maintenance actions

**Screen 2 — Equipment Detail (5 components):**
- `equipment-detail.tsx` — orchestrator with tab toggle
- `equipment-header.tsx` — name, code, location, status badge
- `maintenance-progress.tsx` — progress bar for maintenance completion %
- `top-nodes.tsx` — top sensor groups with status and navigation links
- `equipment-history.tsx` — combined state + action history table with pagination

**Screen 3 — Sensor Group Detail (6 components):**
- `sensor-group-detail.tsx` — orchestrator
- `sensor-group-header.tsx` — name, status badge, breadcrumb links back to equipment
- `node-image.tsx` — image with fallback placeholder
- `sensor-list.tsx` — table of sensor readings with colour-coded status
- `ai-diagnosis.tsx` — fires assistant API on mount; displays streaming diagnosis text

## Verification Results

### pnpm build

```
✓ Compiled successfully in 3.5s
✓ Finished TypeScript in 2.5s
✓ Collecting page data (8/8)
✓ Generating static pages (8/8)

Route (app)
○  /dashboard         (static)
ƒ  /dashboard/equipment/[equipment_id]           (dynamic)
ƒ  /dashboard/equipment/[equipment_id]/nodes/[sensor_group_id]  (dynamic)
```

**Result: PASSED**

### pnpm lint

Two `react-hooks/set-state-in-effect` errors were found and fixed in:
- `equipment-detail.tsx` — removed synchronous `setLoading(true)` / `setEquipment(null)` from effect body; moved `setLoading(false)` into `.then()` / `.catch()` callbacks
- `sensor-group-detail.tsx` — same fix

**Result: PASSED (0 errors, 0 warnings)**

### Backend unit tests

```
60 passed in 0.78s
```

All endpoints exercised by the dashboard are covered:
- `test_dashboard_api.py` — plant overview, state feed, action feed
- `test_equipment_api.py` — list, detail, history
- `test_sensor_groups_api.py` — sensor group detail
- `test_assistant_api.py` — AI diagnosis

**Result: PASSED**

## Drill-Down Navigation

```
/dashboard
  ↓ click equipment in "Worst performers" or state feed
/dashboard/equipment/{equipment_id}
  ↓ click sensor group in "Top nodes" tab
/dashboard/equipment/{equipment_id}/nodes/{sensor_group_id}
```

Each level has breadcrumb links to navigate back up the hierarchy.
