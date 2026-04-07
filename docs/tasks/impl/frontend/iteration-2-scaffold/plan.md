# Iteration 02: Frontend Scaffold — Plan

## Goal

Initialize the frontend project and set up base layout with theme switching, authentication, and navigation.

## Scope of Work

### 1. CORS — Backend Preparation
- Add CORS middleware to the FastAPI backend (`backend/src/maintenance_backend/app.py`) allowing the frontend dev origin (`http://localhost:3000`).
- Ensure preflight OPTIONS requests are handled correctly.

### 2. API Client & Types
- `frontend/src/lib/api/types.ts` — TypeScript types mirroring all backend response schemas (auth, dashboard, equipment, sensor groups, locations, admin, assistant).
- `frontend/src/lib/api/client.ts` — low-level HTTP client using `fetch`, attaches `Authorization: Bearer <token>` header when a token is present in localStorage.
- `frontend/src/lib/api/endpoints.ts` — typed wrappers for every backend endpoint.

### 3. Auth Context
- `frontend/src/lib/auth/context.tsx` — React context providing `user`, `token`, `isAuthenticated`, `isLoading`, `login`, `logout`.
- On mount: reads `auth_token` from localStorage, validates via `GET /api/v1/auth/me`; sets token/user in state only after the async call completes (avoids synchronous setState-in-effect lint violation).
- `login()`: calls `POST /api/v1/auth/login`, stores `access_token` in localStorage.

### 4. Login Page
- `frontend/src/app/(auth)/login/page.tsx` — clean login form accepting a Telegram username.
- Redirects to `/dashboard` on success.

### 5. Main Layout with Sidebar
- `frontend/src/app/(main)/layout.tsx` — protected layout that redirects unauthenticated users to `/login`.
- `frontend/src/components/layout/Sidebar.tsx` — collapsible sidebar with role-based navigation links (Dashboard, Chat, Admin for admin/operator roles).
- `frontend/src/components/layout/Header.tsx` — top bar with user display name, logout button, and theme toggle.
- `frontend/src/components/layout/ThemeProvider.tsx` — `next-themes` provider.

### 6. Placeholder Pages
- `/dashboard` — "Dashboard" placeholder.
- `/chat` — "Chat" placeholder.
- `/admin` — "Admin" placeholder (visible for admin/operator).

### 7. Floating Chat Widget Stub
- `frontend/src/components/chat/ChatWidget.tsx` — floating button in the bottom-right corner; clicking opens a "coming soon" panel stub.

### 8. Makefile Commands
- `make web-install` — `cd frontend && pnpm install`
- `make web-dev` — `cd frontend && pnpm dev`
- `make web-build` — `cd frontend && pnpm build`
- `make web-lint` — `cd frontend && pnpm lint`

## Definition of Done

- `pnpm build` passes with zero errors.
- `pnpm lint` passes with no errors.
- Backend tests (60 tests) pass including CORS tests.
- Backend lint (`ruff check`) is clean.
- Auth token field `access_token` matches between frontend types and backend schema.
