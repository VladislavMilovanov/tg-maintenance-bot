---
name: vercel-react-best-practices
description: React patterns, hooks best practices, state management strategies (useState/useReducer/context/zustand), performance optimization (memo, useMemo, useCallback, lazy loading), and error boundaries. Use when building or reviewing React component architecture.
---

# Vercel React Best Practices

Production-grade React patterns endorsed by the Vercel ecosystem. Covers component design, hooks discipline, state management trade-offs, and performance optimization techniques.

## When to Use This Skill

- Designing or reviewing React component architecture
- Choosing between local state, context, or external state managers
- Optimizing re-render performance in large component trees
- Writing clean, testable custom hooks
- Implementing error boundaries and graceful fallbacks
- Setting up code-splitting and lazy loading
- Debugging stale closures, infinite loops, or unnecessary re-renders

## Core Concepts

### Component Design Principles

**Single Responsibility**: Each component does one thing. Split when:
- A component has more than one reason to change
- Internal state is unrelated to rendering logic
- A chunk of JSX is reused in multiple places

**Composition over configuration**: Prefer children/slots over deeply nested prop APIs.

**Controlled vs Uncontrolled**: Default to controlled for form inputs that need validation or cross-field interaction; uncontrolled for simple, isolated inputs where you only need the value on submit.

## Component Patterns

### Pattern 1: Compound Components

```tsx
// Flexible composition without prop drilling
interface TabsContextValue {
  activeTab: string
  setActiveTab: (tab: string) => void
}

const TabsContext = React.createContext<TabsContextValue | null>(null)

function useTabs() {
  const ctx = React.useContext(TabsContext)
  if (!ctx) throw new Error("useTabs must be used within <Tabs>")
  return ctx
}

function Tabs({ defaultTab, children }: { defaultTab: string; children: React.ReactNode }) {
  const [activeTab, setActiveTab] = React.useState(defaultTab)
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div>{children}</div>
    </TabsContext.Provider>
  )
}

function Tab({ id, children }: { id: string; children: React.ReactNode }) {
  const { activeTab, setActiveTab } = useTabs()
  return (
    <button
      role="tab"
      aria-selected={activeTab === id}
      onClick={() => setActiveTab(id)}
    >
      {children}
    </button>
  )
}

function TabPanel({ id, children }: { id: string; children: React.ReactNode }) {
  const { activeTab } = useTabs()
  if (activeTab !== id) return null
  return <div role="tabpanel">{children}</div>
}

Tabs.Tab = Tab
Tabs.Panel = TabPanel

// Usage:
// <Tabs defaultTab="overview">
//   <Tabs.Tab id="overview">Overview</Tabs.Tab>
//   <Tabs.Panel id="overview"><Overview /></Tabs.Panel>
// </Tabs>
```

### Pattern 2: Render Props / Children as Function

```tsx
// When you need to share behavior without dictating UI
interface DataFetcherProps<T> {
  url: string
  children: (state: { data: T | null; loading: boolean; error: Error | null }) => React.ReactNode
}

function DataFetcher<T>({ url, children }: DataFetcherProps<T>) {
  const [data, setData] = React.useState<T | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<Error | null>(null)

  React.useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetch(url)
      .then(r => r.json())
      .then(d => { if (!cancelled) { setData(d); setLoading(false) } })
      .catch(e => { if (!cancelled) { setError(e); setLoading(false) } })
    return () => { cancelled = true }
  }, [url])

  return <>{children({ data, loading, error })}</>
}
```

## Hooks Best Practices

### Custom Hooks

Extract reusable stateful logic into hooks prefixed with `use`:

```tsx
// hooks/useLocalStorage.ts
function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = React.useState<T>(() => {
    if (typeof window === "undefined") return initialValue
    try {
      const item = window.localStorage.getItem(key)
      return item ? (JSON.parse(item) as T) : initialValue
    } catch {
      return initialValue
    }
  })

  const setValue = React.useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.error(error)
    }
  }, [key, storedValue])

  return [storedValue, setValue] as const
}
```

### useEffect Discipline

```tsx
// GOOD: cleanup prevents stale updates and memory leaks
React.useEffect(() => {
  let cancelled = false

  async function load() {
    const data = await fetchData(id)
    if (!cancelled) setData(data)
  }

  load()
  return () => { cancelled = true }
}, [id]) // stable dependency

// BAD: object/array created in render as dependency causes infinite loop
React.useEffect(() => {
  fetchData(options) // options = { page: 1 } re-created each render
}, [options]) // ← triggers every render

// FIX: stabilize with useMemo or move the literal inside the effect
const stableOptions = React.useMemo(() => ({ page: 1 }), [])
```

### useReducer for Complex State

```tsx
type State = {
  status: "idle" | "loading" | "success" | "error"
  data: User[] | null
  error: string | null
}

type Action =
  | { type: "FETCH_START" }
  | { type: "FETCH_SUCCESS"; payload: User[] }
  | { type: "FETCH_ERROR"; payload: string }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "FETCH_START":
      return { ...state, status: "loading", error: null }
    case "FETCH_SUCCESS":
      return { status: "success", data: action.payload, error: null }
    case "FETCH_ERROR":
      return { ...state, status: "error", error: action.payload }
    default:
      return state
  }
}

function UserList() {
  const [state, dispatch] = React.useReducer(reducer, {
    status: "idle",
    data: null,
    error: null,
  })

  // ...
}
```

## State Management

### Decision Matrix

| Scope | Solution | When |
|-------|----------|------|
| Component | `useState` / `useReducer` | Local UI state, form fields, toggles |
| Subtree | React Context | Theme, auth user, locale — low-frequency updates |
| App-wide / frequent | Zustand | Shopping cart, notifications, real-time data |
| Server state | TanStack Query | Remote data, caching, background refetching |

### Context — Do's and Don'ts

```tsx
// DO: separate contexts by update frequency
const UserContext = React.createContext<User | null>(null)
const ThemeContext = React.createContext<"light" | "dark">("light")

// DON'T: put everything in one giant context
// const AppContext = React.createContext({ user, theme, cart, notifications, ... })
// ↑ Every consumer re-renders on any field change

// DO: memoize context value to prevent unnecessary re-renders
function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null)

  const value = React.useMemo(() => ({ user, setUser }), [user])

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>
}
```

### Zustand

```tsx
// store/cart.ts
import { create } from "zustand"
import { persist } from "zustand/middleware"

interface CartItem {
  id: string
  quantity: number
  price: number
}

interface CartStore {
  items: CartItem[]
  addItem: (item: CartItem) => void
  removeItem: (id: string) => void
  total: () => number
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      addItem: (item) =>
        set((state) => {
          const existing = state.items.find((i) => i.id === item.id)
          if (existing) {
            return {
              items: state.items.map((i) =>
                i.id === item.id ? { ...i, quantity: i.quantity + item.quantity } : i
              ),
            }
          }
          return { items: [...state.items, item] }
        }),
      removeItem: (id) =>
        set((state) => ({ items: state.items.filter((i) => i.id !== id) })),
      total: () => get().items.reduce((sum, i) => sum + i.price * i.quantity, 0),
    }),
    { name: "cart-storage" }
  )
)
```

## Performance Optimization

### React.memo — Use Sparingly

```tsx
// Only memo when the component is expensive AND receives stable props
const ExpensiveRow = React.memo(function ExpensiveRow({ data }: { data: RowData }) {
  // Heavy computation or large subtree
  return <tr>...</tr>
})

// Custom comparison
const TableRow = React.memo(
  function TableRow({ row }: { row: Row }) { return <tr>...</tr> },
  (prev, next) => prev.row.id === next.row.id && prev.row.updatedAt === next.row.updatedAt
)
```

### useMemo and useCallback

```tsx
function FilteredList({ items, filter }: { items: Item[]; filter: string }) {
  // useMemo: expensive derivation
  const filtered = React.useMemo(
    () => items.filter((item) => item.name.toLowerCase().includes(filter.toLowerCase())),
    [items, filter]
  )

  // useCallback: stable reference for child memo or effect dependency
  const handleSelect = React.useCallback((id: string) => {
    // ...
  }, []) // empty deps — no closure over changing values

  return <List items={filtered} onSelect={handleSelect} />
}
```

**Rule of thumb**: Don't add `useMemo`/`useCallback` by default. Add when:
1. You measure an actual render performance problem
2. The function/value is a dependency of `useEffect`
3. The function is passed to a `React.memo` child

### Code Splitting with React.lazy

```tsx
import React, { Suspense } from "react"

const HeavyChart = React.lazy(() => import("./HeavyChart"))
const AdminPanel = React.lazy(() => import("./AdminPanel"))

function Dashboard({ isAdmin }: { isAdmin: boolean }) {
  return (
    <div>
      <Suspense fallback={<ChartSkeleton />}>
        <HeavyChart />
      </Suspense>

      {isAdmin && (
        <Suspense fallback={<div>Loading admin panel...</div>}>
          <AdminPanel />
        </Suspense>
      )}
    </div>
  )
}
```

## Error Boundaries

```tsx
// ErrorBoundary must be a class component
interface Props {
  fallback: React.ReactNode
  children: React.ReactNode
  onError?: (error: Error, info: React.ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
}

class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    this.props.onError?.(error, info)
    // Log to error reporting service
  }

  render() {
    if (this.state.hasError) return this.props.fallback
    return this.props.children
  }
}

// Usage with reset capability
function ResetableErrorBoundary({ children }: { children: React.ReactNode }) {
  const [key, setKey] = React.useState(0)
  return (
    <ErrorBoundary
      key={key}
      fallback={
        <div>
          <p>Something went wrong.</p>
          <button onClick={() => setKey(k => k + 1)}>Try again</button>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  )
}
```

## Best Practices

1. **Collocate state** as close to where it's used as possible — avoid lifting prematurely
2. **Derive, don't sync** — compute derived values in render rather than storing them in state
3. **Keys on lists** — use stable IDs, never array indices for reorderable lists
4. **Avoid anonymous functions in JSX** when passing to memoized children — use `useCallback`
5. **TypeScript strict mode** — enable `strict: true` in `tsconfig.json`
6. **Avoid prop drilling beyond 2 levels** — reach for composition or context
7. **Refs for DOM, not state** — `useRef` for imperative DOM access, not as a workaround for stale closures
8. **Test behavior, not implementation** — React Testing Library over snapshot tests

## Common Pitfalls

- **Stale closures in useEffect**: capture fresh values via refs or include in deps array
- **State updates in unmounted components**: use cleanup flags or AbortController
- **Context as a performance optimization**: context re-renders all consumers on value change
- **Mutating state directly**: always return new objects/arrays from state updaters
- **Missing keys causing reconciliation bugs**: every list item needs a stable, unique key
- **useEffect for derived data**: compute synchronously in render, not in effects
- **Over-using useReducer**: `useState` is fine for simple boolean/string/number state
