# Iteration 6: Full-Page Chat — Plan

## Goal

Implement a full-screen chat page at `/chat` as a dedicated navigation item, reusing the components and hook already built in Iteration 5 (floating chat widget).

## Scope

### 1. Route: `/chat`
- New App Router page at `src/app/(main)/chat/page.tsx`
- Negate the `p-6` padding from the `(main)` layout so the chat fills the entire viewport height
- Use `h-[calc(100vh_-_var(--header-height,4rem))]` to fill available space

### 2. Sessions sidebar (`chat-sessions-sidebar.tsx`)
- Collapsible sidebar (desktop: `w-64` / `w-12`; mobile: fixed overlay with `z-30`)
- Lists all in-memory chat sessions with title and relative timestamp
- "New chat" button creates a fresh session
- Toggle button to collapse/expand the sidebar on desktop
- On mobile: opens as a slide-over panel with a semi-transparent backdrop

### 3. Full-page chat (`chat-page.tsx`)
- `SessionChatArea` inner component — mounts a fresh `useChat` instance per session via `key=` prop
  - Seeds display messages from stored session data until the user interacts
  - Reports back `messages` and `conversationId` to the parent on each change
  - Auto-titles the session from the first message (truncated to 40 chars)
- `ChatPage` outer component — manages `SessionData[]` state and routes to the active session
- Responsive sidebar: desktop toggle, mobile overlay with backdrop
- Reuses `ChatMessageList`, `ChatInput`, `useChat` from Iteration 5 without modification

## Component Reuse from Iteration 5

| Component | Reused as-is |
|-----------|-------------|
| `use-chat.ts` | ✅ |
| `chat-message-list.tsx` | ✅ |
| `chat-input.tsx` | ✅ |
| `chat-widget.tsx` | ✅ (floating widget unchanged) |

## Files to Create/Modify

| File | Action |
|------|--------|
| `src/app/(main)/chat/page.tsx` | Create — thin route wrapper |
| `src/components/chat/chat-page.tsx` | Create — main page component with session management |
| `src/components/chat/chat-sessions-sidebar.tsx` | Create — collapsible sessions sidebar |

## Architecture Decisions

- **In-memory sessions** — no persistence to backend required for this iteration; sessions live in React state
- **`key=` remount pattern** — switching sessions remounts `SessionChatArea` with a new `useChat` instance, keeping session isolation simple
- **Mobile-first sidebar** — sidebar is hidden by default on `max-width: 767px` and rendered as a fixed overlay
