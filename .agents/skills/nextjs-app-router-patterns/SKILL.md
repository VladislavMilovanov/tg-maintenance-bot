---
name: nextjs-app-router-patterns
description: Next.js App Router patterns including file-based routing, React Server Components vs Client Components, layouts, loading/error boundaries, data fetching with server actions, metadata API, parallel/intercepting routes, and middleware. Use when building or architecting Next.js 13+ applications with the App Router.
---

# Next.js App Router Patterns

Comprehensive patterns for the Next.js App Router (Next.js 13+). Covers file conventions, React Server Components, data fetching strategies, routing patterns, and production best practices.

## When to Use This Skill

- Starting a new Next.js project with the App Router
- Migrating from the Pages Router to the App Router
- Designing file structure and routing architecture
- Choosing between Server Components and Client Components
- Implementing data fetching: RSC fetch, server actions, route handlers
- Setting up layouts, loading states, and error handling
- Configuring metadata, OG images, and SEO
- Implementing parallel routes, intercepting routes, or route groups

## Core Concepts

### App Router vs Pages Router

The App Router (`app/` directory) introduces:
- **React Server Components** by default — zero JS bundle impact
- **Nested layouts** that preserve state across navigations
- **Streaming** via `loading.tsx` and `Suspense`
- **Server Actions** — async functions that run on the server, called from the client
- **Collocated data fetching** — fetch data inside the component that needs it

### Component Rendering Model

```
Server Components (default in app/)      Client Components ("use client")
─────────────────────────────────        ──────────────────────────────────
✓ Access server resources directly       ✓ useState, useEffect, hooks
✓ No JavaScript sent to client           ✓ Event handlers (onClick, etc.)
✓ Async/await in component body          ✓ Browser APIs
✓ Direct database/filesystem access      ✓ Third-party client libraries
✗ No React hooks                         ✗ No async component body
✗ No browser APIs                        ✗ Larger JS bundle
```

**Key rule**: Server Components can import Client Components, but Client Components cannot import Server Components (they can receive them as `children` props).

## File Conventions

### Directory Structure

```
app/
├── (marketing)/           # Route group — no URL segment
│   ├── layout.tsx         # Layout for marketing pages only
│   ├── page.tsx           # → /
│   └── about/
│       └── page.tsx       # → /about
├── (app)/                 # Authenticated app group
│   ├── layout.tsx         # Authenticated layout with nav
│   ├── dashboard/
│   │   ├── page.tsx       # → /dashboard
│   │   ├── loading.tsx    # Streaming skeleton
│   │   └── error.tsx      # Error boundary for /dashboard
│   └── settings/
│       └── page.tsx       # → /settings
├── api/
│   └── webhook/
│       └── route.ts       # Route handler → POST /api/webhook
├── layout.tsx             # Root layout (required)
├── not-found.tsx          # Custom 404
└── global-error.tsx       # Root-level error boundary
```

### Special Files Reference

| File | Purpose |
|------|---------|
| `page.tsx` | Route segment UI, makes a route publicly accessible |
| `layout.tsx` | Shared UI wrapper, preserves state on navigation |
| `loading.tsx` | Instant loading skeleton (Suspense boundary) |
| `error.tsx` | Error boundary for the segment (`"use client"` required) |
| `not-found.tsx` | Renders when `notFound()` is called |
| `template.tsx` | Like layout but re-mounts on navigation |
| `route.ts` | API endpoint (replaces pages/api) |
| `middleware.ts` | Runs before request (root-level only) |

## Routing Patterns

### Dynamic Routes

```tsx
// app/blog/[slug]/page.tsx
interface PageProps {
  params: Promise<{ slug: string }>
  searchParams: Promise<{ page?: string }>
}

export default async function BlogPost({ params, searchParams }: PageProps) {
  const { slug } = await params
  const { page = "1" } = await searchParams

  const post = await getPostBySlug(slug)
  if (!post) notFound()

  return <article>{post.content}</article>
}

// Generate static params at build time
export async function generateStaticParams() {
  const posts = await getAllPosts()
  return posts.map((post) => ({ slug: post.slug }))
}

// Dynamic metadata
export async function generateMetadata({ params }: PageProps) {
  const { slug } = await params
  const post = await getPostBySlug(slug)
  return {
    title: post?.title ?? "Post not found",
    description: post?.excerpt,
    openGraph: {
      images: [post?.coverImage ?? "/og-default.png"],
    },
  }
}
```

### Route Groups

```
app/
├── (auth)/
│   ├── login/page.tsx      # → /login (no "(auth)" in URL)
│   └── register/page.tsx   # → /register
└── (dashboard)/
    ├── layout.tsx           # Dashboard-only layout
    └── home/page.tsx        # → /home
```

### Parallel Routes

```tsx
// app/layout.tsx
// Render multiple pages simultaneously in a single layout

export default function Layout({
  children,
  team,
  analytics,
}: {
  children: React.ReactNode
  team: React.ReactNode      // @team slot
  analytics: React.ReactNode // @analytics slot
}) {
  return (
    <div>
      {children}
      <div className="grid grid-cols-2">
        {team}
        {analytics}
      </div>
    </div>
  )
}

// app/@team/page.tsx  — rendered in the "team" slot
// app/@analytics/page.tsx — rendered in the "analytics" slot
```

### Intercepting Routes

```
app/
├── photos/
│   └── [id]/
│       └── page.tsx         # Full-page photo view → /photos/123
└── (.)photos/               # (.) = intercept same level
    └── [id]/
        └── page.tsx         # Modal photo view when navigating within app
```

```tsx
// app/(.)photos/[id]/page.tsx
// Shown as a modal when navigating from the feed
// Falls through to the full page on direct URL visit
import { Modal } from "@/components/modal"

export default async function PhotoModal({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const photo = await getPhoto(id)
  return (
    <Modal>
      <img src={photo.url} alt={photo.alt} />
    </Modal>
  )
}
```

## Layouts and Loading

### Root Layout

```tsx
// app/layout.tsx
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { Providers } from "@/components/providers"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: { template: "%s | My App", default: "My App" },
  description: "My application",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

### Nested Layout with Auth Guard

```tsx
// app/(app)/layout.tsx
import { redirect } from "next/navigation"
import { getSession } from "@/lib/auth"
import { Sidebar } from "@/components/sidebar"

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const session = await getSession()
  if (!session) redirect("/login")

  return (
    <div className="flex h-screen">
      <Sidebar user={session.user} />
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  )
}
```

### Loading and Error Boundaries

```tsx
// app/dashboard/loading.tsx — automatically wraps page in Suspense
export default function DashboardLoading() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-8 bg-muted rounded w-1/3" />
      <div className="h-64 bg-muted rounded" />
    </div>
  )
}

// app/dashboard/error.tsx — must be Client Component
"use client"

import { useEffect } from "react"

interface ErrorProps {
  error: Error & { digest?: string }
  reset: () => void
}

export default function DashboardError({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="flex flex-col items-center gap-4 p-8">
      <h2 className="text-xl font-semibold">Something went wrong</h2>
      <button onClick={reset} className="btn-primary">Try again</button>
    </div>
  )
}
```

## Data Fetching

### Server Component Data Fetching

```tsx
// app/products/page.tsx — fetch directly in RSC, no useEffect needed
interface SearchParams {
  category?: string
  page?: string
}

export default async function ProductsPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>
}) {
  const { category, page = "1" } = await searchParams

  // Parallel fetching with Promise.all
  const [products, categories] = await Promise.all([
    getProducts({ category, page: parseInt(page) }),
    getCategories(),
  ])

  return (
    <div>
      <CategoryFilter categories={categories} active={category} />
      <ProductGrid products={products} />
    </div>
  )
}
```

### Server Actions

```tsx
// app/actions/user.ts
"use server"

import { revalidatePath } from "next/cache"
import { redirect } from "next/navigation"
import { z } from "zod"

const UpdateProfileSchema = z.object({
  name: z.string().min(1),
  bio: z.string().max(500).optional(),
})

export async function updateProfile(formData: FormData) {
  const session = await getSession()
  if (!session) throw new Error("Unauthorized")

  const result = UpdateProfileSchema.safeParse({
    name: formData.get("name"),
    bio: formData.get("bio"),
  })

  if (!result.success) {
    return { error: result.error.flatten().fieldErrors }
  }

  await db.user.update({
    where: { id: session.user.id },
    data: result.data,
  })

  revalidatePath("/settings/profile")
  return { success: true }
}

// Usage from a Client Component:
// const [state, formAction] = useActionState(updateProfile, null)
// <form action={formAction}>...</form>
```

### Route Handlers

```ts
// app/api/users/route.ts
import { NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl
  const page = parseInt(searchParams.get("page") ?? "1")

  const users = await getUsers({ page })
  return NextResponse.json(users)
}

export async function POST(request: NextRequest) {
  const body = await request.json()

  const user = await createUser(body)
  return NextResponse.json(user, { status: 201 })
}

// app/api/users/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const user = await getUserById(id)
  if (!user) return NextResponse.json({ error: "Not found" }, { status: 404 })
  return NextResponse.json(user)
}
```

## Metadata API

```tsx
// Static metadata
export const metadata: Metadata = {
  title: "Dashboard",
  description: "Your personal dashboard",
  keywords: ["dashboard", "analytics"],
  authors: [{ name: "Acme Inc" }],
  openGraph: {
    title: "Dashboard",
    description: "Your personal dashboard",
    images: [{ url: "/og/dashboard.png", width: 1200, height: 630 }],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Dashboard",
  },
  robots: { index: true, follow: true },
}

// Dynamic OG image
// app/og/route.tsx
import { ImageResponse } from "next/og"

export const runtime = "edge"

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const title = searchParams.get("title") ?? "My App"

  return new ImageResponse(
    (
      <div style={{ display: "flex", background: "#0f172a", width: "100%", height: "100%" }}>
        <h1 style={{ color: "white", fontSize: 72 }}>{title}</h1>
      </div>
    ),
    { width: 1200, height: 630 }
  )
}
```

## Middleware

```ts
// middleware.ts (root-level, runs on Edge)
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const token = request.cookies.get("token")?.value

  const isAuthRoute = request.nextUrl.pathname.startsWith("/login")
  const isProtected = request.nextUrl.pathname.startsWith("/dashboard")

  if (isProtected && !token) {
    return NextResponse.redirect(new URL("/login", request.url))
  }

  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/dashboard/:path*", "/login"],
}
```

## Best Practices

1. **Default to Server Components** — only add `"use client"` when you need interactivity
2. **Push `"use client"` to leaf nodes** — keep the component tree mostly server-rendered
3. **Fetch at the component level** — RSC makes prop drilling for data unnecessary
4. **Use `Promise.all` for parallel fetches** — don't waterfall independent requests
5. **Prefer server actions over API routes** for form submissions and mutations
6. **`revalidatePath` / `revalidateTag`** after mutations instead of client-side cache invalidation
7. **`generateStaticParams`** for dynamic segments that can be known at build time
8. **Environment variables**: `NEXT_PUBLIC_` prefix only for client-exposed variables

## Common Pitfalls

- **Importing server-only code into Client Components**: use `server-only` package to guard
- **`params` and `searchParams` are now Promises** (Next.js 15+): always `await` them
- **Context providers must be Client Components**: wrap at the lowest possible level
- **`cookies()` and `headers()` make routes dynamic** — be aware of build-time vs runtime implications
- **Forgetting `"use client"` on error.tsx**: it must be a Client Component
- **Using `useRouter` in Server Components**: use `redirect()` from `next/navigation` instead
- **Not handling loading states for slow data**: use `loading.tsx` or explicit `<Suspense>` boundaries
- **Giant root layouts**: split with route groups and nested layouts for better streaming granularity
