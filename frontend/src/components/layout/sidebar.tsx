"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth/context";
import { LayoutDashboard, Shield, MessageSquare, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Дашборд", icon: LayoutDashboard },
  { href: "/chat", label: "Чат", icon: MessageSquare },
];

const adminItems = [
  { href: "/admin", label: "Админ", icon: Shield },
];

interface SidebarProps {
  onClose?: () => void;
}

export function Sidebar({ onClose }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="w-64 border-r border-border bg-card flex flex-col h-full">
      {/* Logo / brand section */}
      <div className="p-4 border-b border-border">
        <h1 className="text-lg font-semibold text-foreground">Мониторинг</h1>
        <p className="text-xs text-muted-foreground">Система управления оборудованием</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-1" aria-label="Основная навигация">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            onClick={onClose}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
              pathname.startsWith(item.href)
                ? "bg-accent text-accent-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-accent/50",
            )}
          >
            <item.icon className="h-4 w-4" aria-hidden="true" />
            {item.label}
          </Link>
        ))}

        {/* Admin section - only if role is admin */}
        {user?.role === "admin" &&
          adminItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                pathname.startsWith(item.href)
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent/50",
              )}
            >
              <item.icon className="h-4 w-4" aria-hidden="true" />
              {item.label}
            </Link>
          ))}
      </nav>

      {/* User info + logout at bottom */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center justify-between">
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-foreground truncate">
              {user?.display_name || "User"}
            </p>
            <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
          </div>
          <button
            onClick={logout}
            className="p-2 text-muted-foreground hover:text-foreground transition-colors shrink-0 min-w-[44px] min-h-[44px] flex items-center justify-center"
            aria-label="Выйти из системы"
          >
            <LogOut className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </div>
    </aside>
  );
}
