"use client";

import { Button } from "@/components/ui/button";
import { Plus, MessageSquare, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ChatSession {
  id: string;
  title: string;
  createdAt: Date;
}

interface ChatSessionsSidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  isOpen: boolean;
  onToggle: () => void;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
}

function formatTime(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return "Только что";
  if (minutes < 60) return `${minutes} мин. назад`;
  if (hours < 24) return `${hours} ч. назад`;
  return `${days} д. назад`;
}

export function ChatSessionsSidebar({
  sessions,
  activeSessionId,
  isOpen,
  onToggle,
  onSelectSession,
  onNewSession,
}: ChatSessionsSidebarProps) {
  return (
    <div
      className={cn(
        "flex flex-col border-r border-border bg-card transition-all duration-200 shrink-0",
        isOpen ? "w-64" : "w-12",
      )}
    >
      {/* Sidebar header */}
      <div className="flex items-center justify-between px-2 py-3 border-b border-border shrink-0">
        {isOpen && (
          <span className="text-sm font-semibold text-foreground ml-1 truncate">
            Сессии
          </span>
        )}
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 shrink-0 ml-auto"
          onClick={onToggle}
          aria-label={isOpen ? "Свернуть панель" : "Развернуть панель"}
        >
          {isOpen ? (
            <PanelLeftClose className="h-4 w-4" />
          ) : (
            <PanelLeftOpen className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* New chat button */}
      <div className="px-2 py-2 shrink-0">
        <Button
          variant="outline"
          size="sm"
          className={cn(
            "w-full gap-2 justify-start",
            !isOpen && "justify-center px-0",
          )}
          onClick={onNewSession}
          aria-label="Новый чат"
        >
          <Plus className="h-4 w-4 shrink-0" />
          {isOpen && <span className="truncate">Новый чат</span>}
        </Button>
      </div>

      {/* Sessions list */}
      {isOpen && (
        <div className="flex-1 min-h-0 overflow-y-auto">
          <div className="px-2 pb-2 space-y-1">
            {sessions.length === 0 ? (
              <p className="text-xs text-muted-foreground text-center py-4 px-2">
                Нет сессий
              </p>
            ) : (
              sessions.map((session) => (
                <button
                  key={session.id}
                  onClick={() => onSelectSession(session.id)}
                  className={cn(
                    "w-full flex items-start gap-2 rounded-lg px-2 py-2 text-left transition-colors hover:bg-accent",
                    activeSessionId === session.id &&
                      "bg-accent text-accent-foreground",
                  )}
                  aria-label={`Переключиться на сессию: ${session.title}`}
                >
                  <MessageSquare className="h-3.5 w-3.5 shrink-0 mt-0.5 text-muted-foreground" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm leading-tight truncate font-medium">
                      {session.title}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {formatTime(session.createdAt)}
                    </p>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
