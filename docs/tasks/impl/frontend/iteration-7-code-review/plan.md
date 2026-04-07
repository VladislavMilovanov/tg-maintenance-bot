# Iteration 7: Code Quality Review — Plan

## Goal

Conduct a comprehensive code quality review of the frontend codebase and fix all identified issues, covering TypeScript correctness, ESLint compliance, accessibility (a11y), responsive design, and general code hygiene.

## Scope

### 1. TypeScript Strict Check

- Run `npx tsc --noEmit` with the project's strict TypeScript config
- Fix any type errors, implicit `any`, or unsafe casts

### 2. ESLint Compliance

- Run `pnpm lint` (ESLint with Next.js + TypeScript rules)
- Fix all reported errors and warnings

### 3. Accessibility (a11y)

- Audit all interactive elements for missing `aria-label` attributes
- Ensure semantic roles are applied where appropriate (`role="status"`, `role="navigation"`, etc.)
- Validate `<progress>` / progress-bar elements carry correct ARIA attributes (`role="progressbar"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`)
- Verify breadcrumb navigation has `aria-label="Breadcrumb"` on its `<nav>` wrapper
- Confirm tab components carry `aria-label` on `<TabsList>` and related elements

### 4. Responsive Design

- Test all pages at 375 px (mobile), 768 px (tablet), and 1280 px (desktop) breakpoints
- Fix mobile sidebar on `/chat` — should not overflow or block content at 375 px
- Fix chat widget width on small screens — constrain to `max-w-[calc(100vw-2rem)]`
- Fix layout padding on narrow viewports to prevent content clipping

### 5. Code Quality / Hygiene

- Replace `lang="ru"` with `lang="en"` in root `layout.tsx` (project uses English UI)
- Remove dead code and unused imports discovered during review
- Ensure consistent naming conventions across component files

## Files in Scope

| Area | Files |
|------|-------|
| Root layout | `src/app/layout.tsx` |
| Chat page | `src/components/chat/chat-page.tsx`, `src/components/chat/chat-sessions-sidebar.tsx` |
| Chat widget | `src/components/chat/chat-widget.tsx` |
| Dashboard pages | `src/app/(main)/dashboard/**`, `src/components/dashboard/**` |
| Admin page | `src/app/(main)/admin/**`, `src/components/admin/**` |
| Shared UI | `src/components/ui/**` |

## Architecture Decisions

- **No new dependencies** — all fixes use existing Tailwind utilities and shadcn/ui ARIA props
- **Non-breaking changes only** — visual appearance and functionality remain identical after fixes
- **Deferred items** — complex keyboard-navigation traps (e.g. focus lock inside modals) deferred to a dedicated a11y iteration if needed
