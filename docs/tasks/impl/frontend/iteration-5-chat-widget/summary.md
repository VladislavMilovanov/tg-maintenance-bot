# Iteration 5 Summary: Floating Chat Widget

## What was built

A global floating AI assistant chat widget integrated into the main application layout. The widget is always visible on every authenticated page and allows users to ask questions about equipment state in natural language.

### New components

| File | Type | Description |
|------|------|-------------|
| `frontend/src/components/chat/use-chat.ts` | React hook | All chat state and API logic: message list, `conversation_id`, equipment context, error + retry |
| `frontend/src/components/chat/chat-message-list.tsx` | Component | Scrollable bubble list with loading spinner and empty state |
| `frontend/src/components/chat/chat-input.tsx` | Component | Controlled input bar with Enter-to-send and send button |
| `frontend/src/components/chat/chat-widget.tsx` | Component | Floating toggle button + collapsible panel combining all sub-components |
| `frontend/src/components/ui/input.tsx` | UI primitive | shadcn/ui `Input` component (required by `chat-input`) |

### Modified files

| File | Change |
|------|--------|
| `frontend/src/app/(main)/layout.tsx` | Added `<ChatWidget />` import and render |

## Architecture decisions

### Hook-first decomposition (`use-chat.ts`)

All stateful logic lives in a single custom hook. Components are purely presentational. This means iteration 6 (full-screen `/chat` page) can compose the same `use-chat` + `chat-message-list` + `chat-input` without duplicating any business logic.

### Client-side message history

Messages are stored in React state (`useState<ChatMessage[]>`). No server-side persistence is required for the session — the backend tracks conversation context via `conversation_id` which is obtained from the first API response and forwarded on every subsequent request.

### Equipment context from URL

`useEquipmentContext()` (inside `chat-widget.tsx`) reads `usePathname()` and applies a regex match:

```
/\/dashboard\/equipment\/([^/]+)(?:\/nodes\/([^/]+))?/
```

This extracts `equipment_id` and optionally `sensor_group_id` from the current URL. The extracted context is forwarded in every assistant API request, allowing the AI to scope its answers to the currently viewed item without any explicit user action.

### Error handling with retry

Failed sends remove the optimistically-added user message and expose a `retryLast()` function. An inline error banner provides a "Повторить" button wired to `retryLast()`.

### Cancelled-request guard

A `{ value: boolean }` cancellation token is passed into `doSend` so that async state updates are skipped if the widget unmounts or a newer request supersedes the previous one.

## Files created / modified

```
frontend/src/components/chat/
├── use-chat.ts               (new, 115 lines)
├── chat-message-list.tsx     (new, 65 lines)
├── chat-input.tsx            (new, 57 lines)
└── chat-widget.tsx           (new, 104 lines)

frontend/src/components/ui/
└── input.tsx                 (new, shadcn/ui primitive)

frontend/src/app/(main)/layout.tsx   (modified — ChatWidget added)
```

## Verification results

| Check | Result |
|-------|--------|
| `pnpm build` | ✅ Compiled successfully (Turbopack, Next.js 16.2.2) |
| `pnpm lint` | ✅ No lint errors |
| `uv run pytest backend/tests/ -x -q` (with `PYTHONPATH=backend/src`) | ✅ 60 passed in 0.72 s |
