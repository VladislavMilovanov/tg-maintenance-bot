"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { MessageSquare, X } from "lucide-react";
import { useAuth } from "@/lib/auth/context";
import { useChat } from "./use-chat";
import { ChatMessageList } from "./chat-message-list";
import { ChatInput } from "./chat-input";
import type { EquipmentContext } from "@/lib/api/types";

type PageContext = "dashboard" | "equipment" | "sensor-group";

const SUGGESTED_QUESTIONS: Record<PageContext, string[]> = {
  dashboard: ["Какие проблемы сейчас?", "Что изменилось за неделю?", "Общее состояние площадки?"],
  equipment: ["Какое состояние оборудования?", "Что рекомендуете?", "Какие узлы в риске?"],
  "sensor-group": ["Какой диагноз узла?", "Что делать?", "Какие возможные причины?"],
};

function usePageContext(): { pageType: PageContext; equipmentContext: EquipmentContext | null } {
  const pathname = usePathname();

  // Match /dashboard/equipment/[id] or /dashboard/equipment/[id]/nodes/[sg_id]
  const equipmentMatch = pathname.match(
    /\/dashboard\/equipment\/([^/]+)(?:\/nodes\/([^/]+))?/,
  );

  if (!equipmentMatch) return { pageType: "dashboard", equipmentContext: null };

  const equipmentId = equipmentMatch[1];
  const sensorGroupId = equipmentMatch[2];

  return {
    pageType: sensorGroupId ? "sensor-group" : "equipment",
    equipmentContext: {
      equipment_id: equipmentId,
      sensor_group_ids: sensorGroupId ? [sensorGroupId] : undefined,
    },
  };
}

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const { user } = useAuth();
  const { pageType, equipmentContext } = usePageContext();

  const { messages, isLoading, error, sendMessage, retryLast } = useChat({
    user,
    equipmentContext,
  });

  return (
    <>
      {/* Chat panel */}
      {isOpen && (
        <div className="fixed bottom-20 right-4 left-4 sm:left-auto sm:right-6 z-50 sm:w-[400px] h-[500px] rounded-xl border border-border bg-card shadow-2xl flex flex-col overflow-hidden">
          {/* Header */}
          <div className="px-4 py-3 border-b border-border flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <h3 className="text-sm font-semibold text-foreground">
                AI Ассистент
              </h3>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-muted-foreground hover:text-foreground transition-colors"
              aria-label="Закрыть чат"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Context indicator */}
          {pageType !== "dashboard" && (
            <div className="px-3 py-1.5 text-xs text-muted-foreground bg-muted/30 border-b border-border shrink-0">
              {pageType === "equipment" ? "Контекст: страница оборудования" : "Контекст: страница узла"}
            </div>
          )}

          {/* Message list */}
          <ChatMessageList messages={messages} isLoading={isLoading} />

          {/* Suggested questions - show when no messages */}
          {messages.length === 0 && (
            <div className="px-3 py-2 flex flex-wrap gap-2 border-t border-border shrink-0">
              {SUGGESTED_QUESTIONS[pageType].map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  disabled={isLoading}
                  className="text-xs px-3 py-1.5 rounded-full border border-border bg-muted/50 text-foreground hover:bg-muted transition-colors disabled:opacity-50"
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {/* Error banner */}
          {error && (
            <div className="mx-3 mb-2 px-3 py-2 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs flex items-center justify-between gap-2 shrink-0">
              <span className="flex-1 min-w-0 truncate">{error}</span>
              <button
                onClick={() => retryLast()}
                className="shrink-0 underline underline-offset-2 hover:no-underline font-medium"
                disabled={isLoading}
              >
                Повторить
              </button>
            </div>
          )}

          {/* Input */}
          <ChatInput
            onSend={sendMessage}
            isLoading={isLoading}
            disabled={!user}
          />
        </div>
      )}

      {/* Floating toggle button */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="fixed bottom-6 right-4 sm:right-6 z-50 h-12 w-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center shadow-lg hover:opacity-90 transition-opacity"
        aria-label={isOpen ? "Закрыть чат" : "Открыть чат"}
      >
        {isOpen ? (
          <X className="h-5 w-5" />
        ) : (
          <MessageSquare className="h-5 w-5" />
        )}
      </button>
    </>
  );
}
