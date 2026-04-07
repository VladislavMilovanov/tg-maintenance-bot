---
name: shadcn
description: shadcn/ui component patterns, theming with CSS variables, dark mode, accessibility, composition patterns, and form integration with react-hook-form + zod. Use when building React UIs with shadcn/ui components or customizing the design system.
---

# shadcn/ui

shadcn/ui is a collection of re-usable components built on top of Radix UI primitives and Tailwind CSS. Unlike a traditional component library, you own the code — components are copied into your project and fully customizable.

## When to Use This Skill

- Installing and using shadcn/ui components in a React/Next.js project
- Customizing the design system via CSS variables and Tailwind config
- Implementing dark mode with CSS variable-based theming
- Building accessible UI components with Radix UI primitives
- Composing complex UI from primitive building blocks
- Integrating forms with react-hook-form and zod validation
- Extending or creating custom variants using `cva` (class-variance-authority)

## Core Concepts

### Component Architecture

shadcn/ui components are **not a dependency** — they are source files copied into `components/ui/`. This means:

- Full ownership and customization freedom
- No breaking changes from upstream library updates
- Components are composable primitives, not monolithic widgets
- Built on Radix UI for accessible behavior, styled with Tailwind CSS

### CSS Variable Theming

The design system is driven by CSS custom properties mapped in `tailwind.config.ts`:

```css
/* globals.css */
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... dark variants for all tokens */
  }
}
```

```ts
// tailwind.config.ts
import { type Config } from "tailwindcss"

const config: Config = {
  darkMode: ["class"],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        // ... map all CSS variables
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
}
```

## Installation Patterns

### CLI Installation

```bash
# Initialize shadcn in a Next.js project
npx shadcn@latest init

# Add individual components
npx shadcn@latest add button
npx shadcn@latest add form input label
npx shadcn@latest add dialog sheet drawer
npx shadcn@latest add table data-table
npx shadcn@latest add toast sonner
```

### components.json Configuration

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

## Component Patterns

### Pattern 1: cn() Utility

Always use the `cn()` utility for conditional class merging:

```ts
// lib/utils.ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

```tsx
// Usage in components
import { cn } from "@/lib/utils"

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "destructive" | "outline"
  isLoading?: boolean
}

export function Button({ className, variant = "default", isLoading, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-md text-sm font-medium",
        variant === "destructive" && "bg-destructive text-destructive-foreground",
        isLoading && "opacity-50 cursor-not-allowed",
        className
      )}
      disabled={isLoading}
      {...props}
    />
  )
}
```

### Pattern 2: Class Variance Authority (CVA)

Use `cva` to define component variants cleanly:

```tsx
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
        secondary: "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive: "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
        outline: "text-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}
```

### Pattern 3: Composition with Radix Primitives

```tsx
// Custom Dialog built on shadcn Dialog primitive
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

interface ConfirmDialogProps {
  title: string
  description: string
  onConfirm: () => void
  children: React.ReactNode
}

export function ConfirmDialog({ title, description, onConfirm, children }: ConfirmDialogProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline">Cancel</Button>
          <Button variant="destructive" onClick={onConfirm}>Confirm</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

## Form Integration with react-hook-form + zod

### Pattern: Full Form with Validation

```tsx
"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const formSchema = z.object({
  username: z.string().min(2, "Username must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  role: z.enum(["admin", "user", "viewer"], {
    required_error: "Please select a role",
  }),
})

type FormValues = z.infer<typeof formSchema>

export function UserForm({ onSubmit }: { onSubmit: (data: FormValues) => Promise<void> }) {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      email: "",
    },
  })

  const { isSubmitting } = form.formState

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="johndoe" {...field} />
              </FormControl>
              <FormDescription>This is your public display name.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" placeholder="john@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="role"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Role</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a role" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="user">User</SelectItem>
                  <SelectItem value="viewer">Viewer</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : "Save"}
        </Button>
      </form>
    </Form>
  )
}
```

## Dark Mode

### next-themes Integration

```tsx
// app/providers.tsx
"use client"

import { ThemeProvider } from "next-themes"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      {children}
    </ThemeProvider>
  )
}

// components/theme-toggle.tsx
"use client"

import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"

export function ThemeToggle() {
  const { setTheme, theme } = useTheme()

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "light" ? "dark" : "light")}
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
    </Button>
  )
}
```

## Accessibility Best Practices

- **Always use `asChild`** when wrapping interactive elements to avoid nested buttons/links
- **Use `DialogTitle` and `DialogDescription`** — Radix enforces these for screen readers
- **Keyboard navigation** is built into Radix primitives; don't override `onKeyDown` without reason
- **Focus management** is automatic via Radix; use `initialFocus` refs only when needed
- **Color contrast**: All default shadcn themes meet WCAG AA; verify custom themes with a contrast checker
- **`aria-label`** on icon-only buttons: `<Button size="icon" aria-label="Close"><X /></Button>`

## Common Pitfalls

- **Forgetting `"use client"`** on components that use hooks or event handlers with shadcn
- **Importing from wrong path**: import from `@/components/ui/button`, not from `shadcn`
- **Overriding `className` without `cn()`**: merge conflicts cause unexpected styles
- **Using `<button>` inside `<Button>`**: use `asChild` prop instead
- **Not running `npx shadcn@latest add`** after upgrading — components don't auto-update
- **Missing `ThemeProvider`** wrapper causes flash of wrong theme on dark mode
- **Tailwind purge missing `components/ui`**: ensure `tailwind.config.ts` content includes `./components/**/*.{ts,tsx}`
