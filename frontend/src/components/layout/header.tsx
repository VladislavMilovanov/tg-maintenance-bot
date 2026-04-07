"use client";

import { Menu } from "lucide-react";
import { ThemeToggle } from "./theme-toggle";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  onMenuOpen?: () => void;
}

export function Header({ onMenuOpen }: HeaderProps) {
  return (
    <header className="h-14 border-b border-border bg-card flex items-center justify-between px-4 md:px-6 shrink-0">
      <div className="flex items-center gap-2">
        {/* Hamburger — only visible on mobile */}
        {onMenuOpen && (
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden h-9 w-9"
            onClick={onMenuOpen}
            aria-label="Открыть меню навигации"
          >
            <Menu className="h-5 w-5" aria-hidden="true" />
          </Button>
        )}
      </div>
      <ThemeToggle />
    </header>
  );
}
