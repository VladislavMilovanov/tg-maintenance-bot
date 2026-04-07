# Iteration 5 Plan: Floating Chat Widget

## Goal

Implement a global floating AI assistant chat widget accessible from every page of the application.

## Scope

### Components to build

1. **`use-chat.ts`** — Custom React hook encapsulating all chat state and API communication logic:
   - Client-side message history (`ChatMessage[]`)
   - Session-scoped `conversation_id` persistence
   - Equipment context forwarding to the assistant API
   - Error handling with retry support

2. **`chat-message-list.tsx`** — Scrollable message bubble list:
   - User messages (right-aligned, primary color)
   - Assistant messages (left-aligned, muted background)
   - Loading indicator ("Думаю…" spinner)
   - Empty state prompt
   - Auto-scroll to newest message

3. **`chat-input.tsx`** — Message input bar:
   - Controlled text input with Enter-to-send
   - Send button (disabled while loading or input empty)
   - Reusable shadcn/ui `Input` component

4. **`chat-widget.tsx`** — Top-level floating widget:
   - Fixed-position toggle button (bottom-right, `MessageSquare` / `X` icon)
   - Collapsible panel (400 × 500 px, elevated z-index)
   - Equipment context detection via `usePathname()` regex match
   - Inline error banner with retry action
   - Integration of all sub-components

5. **`components/ui/input.tsx`** — shadcn/ui Input primitive (added as dependency)

### API integration

- Endpoint: `POST /api/v1/assistant/messages`
- Request body includes: `channel`, `user`, `message.text`, `conversation_id?`, `equipment_context?`
- `equipment_context` is extracted from URL: `/dashboard/equipment/[id]` and `/dashboard/equipment/[id]/nodes/[sg_id]`

### Layout integration

- `ChatWidget` is placed in `src/app/(main)/layout.tsx` so it appears on all authenticated pages

## Reusability for Iteration 6

`use-chat`, `chat-message-list`, and `chat-input` are designed as standalone, composable units so the full-screen `/chat` page (iteration 6) can reuse them without duplicating business logic.

## Definition of Done

- [ ] Floating button visible on all pages
- [ ] Panel opens/closes on click
- [ ] Messages sent to backend assistant API with correct payload
- [ ] `conversation_id` persisted within session
- [ ] Equipment/sensor-group context forwarded when on detail pages
- [ ] Build passes (`pnpm build`)
- [ ] Lint passes (`pnpm lint`)
- [ ] Backend tests unaffected (60 passing)
