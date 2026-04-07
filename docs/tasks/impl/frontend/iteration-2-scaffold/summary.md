# Iteration 02: Frontend Scaffold — Summary

## What Was Done

### Backend: CORS
- Added `CORSMiddleware` to `backend/src/maintenance_backend/app.py` with origins `http://localhost:3000` and `http://localhost:3001`.
- Allowed methods: `GET, POST, PUT, PATCH, DELETE, OPTIONS`.
- Allowed headers: `Authorization, Content-Type`.
- `allow_credentials=True`.
- Added `backend/tests/test_cors.py` — preflight and regular-request CORS header tests.

### Frontend: API Client & Types
- `frontend/src/lib/api/types.ts` — full TypeScript type library for all backend schemas.  
  **Fix applied (Iteration 2 verification):** `AuthLoginResponse` corrected to use `access_token: string` and `token_type: string` to match `LoginResponse` in `backend/src/maintenance_backend/schemas/auth.py`. Previous version had an incorrect `token: string` field.
- `frontend/src/lib/api/client.ts` — thin `fetch` wrapper; attaches `Authorization: Bearer` header from `localStorage.auth_token`.
- `frontend/src/lib/api/endpoints.ts` — typed async functions for every API endpoint.

### Frontend: Auth Context
- `frontend/src/lib/auth/context.tsx` — React context with `user`, `token`, `isAuthenticated`, `isLoading`, `login`, `logout`.  
  **Fix applied (Iteration 2 verification):** Replaced synchronous `setToken(savedToken)` inside `useEffect` (triggered ESLint `react-hooks/set-state-in-effect`) with a lazy `useState` initializer that reads localStorage once before the first render. Token and user state are now set only inside the async `.then()` callback.

### Frontend: Pages & Layout
- `frontend/src/app/layout.tsx` — root layout with `ThemeProvider` and `AuthProvider`.
- `frontend/src/app/(auth)/login/page.tsx` — login form with Telegram username input; redirects to `/dashboard` on success.
- `frontend/src/app/(main)/layout.tsx` — protected layout; redirects unauthenticated users to `/login`; renders `Sidebar`, `Header`, and floating `ChatWidget`.
- `frontend/src/app/(main)/dashboard/page.tsx` — Dashboard placeholder page.
- `frontend/src/app/(main)/chat/page.tsx` — Chat placeholder page.
- `frontend/src/app/(main)/admin/page.tsx` — Admin placeholder page.
- `frontend/src/app/page.tsx` — root redirect to `/dashboard`.

### Frontend: Layout Components
- `frontend/src/components/layout/ThemeProvider.tsx` — `next-themes` ThemeProvider wrapper.
- `frontend/src/components/layout/Sidebar.tsx` — collapsible sidebar; role-based nav (Admin/Operator see admin link).
- `frontend/src/components/layout/Header.tsx` — top bar with user name, logout, and light/dark theme toggle.

### Frontend: Chat Widget Stub
- `frontend/src/components/chat/ChatWidget.tsx` — floating chat button (bottom-right); clicking toggles a "coming soon" panel stub.

### Makefile
- `make web-install`, `make web-dev`, `make web-build`, `make web-lint` commands added to `Makefile`.

## Files Created / Modified

### Backend
- `backend/src/maintenance_backend/app.py` — CORS middleware added
- `backend/tests/test_cors.py` — new CORS tests

### Frontend (new files)
- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx`
- `frontend/src/app/globals.css`
- `frontend/src/app/(auth)/login/page.tsx`
- `frontend/src/app/(main)/layout.tsx`
- `frontend/src/app/(main)/dashboard/page.tsx`
- `frontend/src/app/(main)/chat/page.tsx`
- `frontend/src/app/(main)/admin/page.tsx`
- `frontend/src/components/layout/ThemeProvider.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/layout/Header.tsx`
- `frontend/src/components/chat/ChatWidget.tsx`
- `frontend/src/lib/api/types.ts`
- `frontend/src/lib/api/client.ts`
- `frontend/src/lib/api/endpoints.ts`
- `frontend/src/lib/auth/context.tsx`
- `frontend/src/lib/utils.ts`

### Config / Tooling
- `Makefile` — web-* targets added
- `frontend/package.json`, `frontend/tsconfig.json`, `frontend/next.config.ts`
- `frontend/components.json` (shadcn config)
- `frontend/.env.local`

## Verification Results

| Check | Result |
|-------|--------|
| `pnpm build` | ✅ Passed — 6 static routes generated, 0 errors |
| `pnpm lint` | ✅ Passed — 0 errors after fixing setState-in-effect |
| Backend tests (`pytest backend/tests/`) | ✅ 60/60 passed (incl. CORS tests) |
| Backend lint (`ruff check backend/src/`) | ✅ All checks passed |
| Auth token field alignment | ✅ Fixed: `access_token` used consistently in types.ts and context.tsx |
