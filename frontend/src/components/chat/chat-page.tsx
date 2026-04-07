"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { useAuth } from "@/lib/auth/context";
import { useChat } from "./use-chat";
import { ChatMessageList } from "./chat-message-list";
import { ChatInput } from "./chat-input";
import {
  ChatSessionsSidebar,
  type ChatSession,
} from "./chat-sessions-sidebar";
import type { ChatMessage } from "./use-chat";
import { Button } from "@/components/ui/button";
import { PanelLeftOpen } from "lucide-react";

// ---------------------------------------------------------------------------
// SessionChatArea — mounts a fresh useChat per session (via key= in parent)
// Syncs messages/conversationId up to parent on every change
// ---------------------------------------------------------------------------

interface SessionChatAreaProps {
  user: ReturnType<typeof useAuth>["user"];
  onMessagesChange: (
    messages: ChatMessage[],
    conversationId: string | null,
  ) => void;
  onFirstMessage: (text: string) => void;
  initialMessages: ChatMessage[];
  initialConversationId: string | null;
}

function SessionChatArea({
  user,
  onMessagesChange,
  onFirstMessage,
  initialMessages,
  initialConversationId,
}: SessionChatAreaProps) {
  const { messages, isLoading, error, sendMessage, retryLast, conversationId } =
    useChat({ user, equipmentContext: null });

  // Overlay: show initial messages until user sends the first message
  const [hasInteracted, setHasInteracted] = useState(false);

  // Sync messages and conversationId up to parent whenever they change
  useEffect(() => {
    if (!hasInteracted) return;
    onMessagesChange(messages, conversationId);
  }, [messages, conversationId, hasInteracted, onMessagesChange]);

  const firstMessageRef = useRef(false);

  const handleSend = useCallback(
    async (text: string) => {
      if (!firstMessageRef.current) {
        firstMessageRef.current = true;
        onFirstMessage(text);
        setHasInteracted(true);
      }
      await sendMessage(text);
    },
    [sendMessage, onFirstMessage],
  );

  // Display: use live messages after interaction, seed messages before
  const displayMessages = hasInteracted ? messages : initialMessages;
  const displayConversationId = hasInteracted
    ? conversationId
    : initialConversationId;
  void displayConversationId; // referenced for future use

  return (
    <div className="flex flex-col flex-1 min-h-0 min-w-0">
      <ChatMessageList messages={displayMessages} isLoading={isLoading} />

      {error && (
        <div className="mx-4 mb-2 px-3 py-2 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center justify-between gap-2 shrink-0">
          <span className="flex-1 min-w-0 truncate">{error}</span>
          <button
            onClick={() => retryLast()}
            className="shrink-0 underline underline-offset-2 hover:no-underline font-medium text-sm"
            disabled={isLoading}
          >
            Повторить
          </button>
        </div>
      )}

      <ChatInput onSend={handleSend} isLoading={isLoading} disabled={!user} />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Per-session stored data
// ---------------------------------------------------------------------------

interface SessionData {
  meta: ChatSession;
  messages: ChatMessage[];
  conversationId: string | null;
}

function createNewSessionData(): SessionData {
  return {
    meta: {
      id: crypto.randomUUID(),
      title: "Новый чат",
      createdAt: new Date(),
    },
    messages: [],
    conversationId: null,
  };
}

// ---------------------------------------------------------------------------
// ChatPage — main exported component
// ---------------------------------------------------------------------------

export function ChatPage() {
  const { user } = useAuth();

  const initialSession = createNewSessionData();
  const [sessions, setSessions] = useState<SessionData[]>([initialSession]);
  const [activeSessionId, setActiveSessionId] = useState<string>(
    initialSession.meta.id,
  );
  const [sidebarOpen, setSidebarOpen] = useState(
    () => typeof window === "undefined" ? true : !window.matchMedia("(max-width: 767px)").matches,
  );
  const [isMobile, setIsMobile] = useState(
    () => typeof window === "undefined" ? false : window.matchMedia("(max-width: 767px)").matches,
  );

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 767px)");

    const handleChange = (e: MediaQueryListEvent) => {
      if (e.matches) {
        setIsMobile(true);
        setSidebarOpen(false);
      } else {
        setIsMobile(false);
      }
    };

    mq.addEventListener("change", handleChange);
    return () => mq.removeEventListener("change", handleChange);
  }, []);

  const activeSession = sessions.find((s) => s.meta.id === activeSessionId);

  const handleSelectSession = useCallback(
    (id: string) => {
      setActiveSessionId(id);
      if (isMobile) setSidebarOpen(false);
    },
    [isMobile],
  );

  const handleNewSession = useCallback(() => {
    const newSession = createNewSessionData();
    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newSession.meta.id);
    if (isMobile) setSidebarOpen(false);
  }, [isMobile]);

  const handleMessagesChange = useCallback(
    (messages: ChatMessage[], conversationId: string | null) => {
      setSessions((prev) =>
        prev.map((s) =>
          s.meta.id === activeSessionId
            ? { ...s, messages, conversationId }
            : s,
        ),
      );
    },
    [activeSessionId],
  );

  const handleFirstMessage = useCallback(
    (text: string) => {
      const title = text.length > 40 ? text.slice(0, 40) + "\u2026" : text;
      setSessions((prev) =>
        prev.map((s) =>
          s.meta.id === activeSessionId
            ? { ...s, meta: { ...s.meta, title } }
            : s,
        ),
      );
    },
    [activeSessionId],
  );

  const sessionMetas = sessions.map((s) => s.meta);

  return (
    <div className="flex h-full min-h-0 overflow-hidden bg-background">
      {/* Mobile overlay when sidebar is open */}
      {isMobile && sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/50"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sessions sidebar */}
      <div
        className={
          isMobile
            ? `fixed inset-y-0 left-0 z-30 transition-transform duration-200 h-full${sidebarOpen ? "" : " -translate-x-full"}`
            : "relative flex-shrink-0"
        }
      >
        <ChatSessionsSidebar
          sessions={sessionMetas}
          activeSessionId={activeSessionId}
          isOpen={isMobile ? true : sidebarOpen}
          onToggle={() => setSidebarOpen((v) => !v)}
          onSelectSession={handleSelectSession}
          onNewSession={handleNewSession}
        />
      </div>

      {/* Chat area */}
      <div className="flex flex-col flex-1 min-h-0 min-w-0">
        {/* Chat header */}
        <div className="px-4 py-3 border-b border-border flex items-center gap-3 shrink-0 bg-card">
          {isMobile && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 shrink-0"
              onClick={() => setSidebarOpen(true)}
              aria-label="Открыть панель сессий"
            >
              <PanelLeftOpen className="h-4 w-4" />
            </Button>
          )}
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500 shrink-0" />
            <h1 className="text-base font-semibold text-foreground truncate">
              {activeSession?.meta.title ?? "AI Ассистент"}
            </h1>
          </div>
        </div>

        {/* Session chat area — keyed to remount useChat on session switch */}
        {activeSession && (
          <SessionChatArea
            key={activeSession.meta.id}
            user={user}
            initialMessages={activeSession.messages}
            initialConversationId={activeSession.conversationId}
            onMessagesChange={handleMessagesChange}
            onFirstMessage={handleFirstMessage}
          />
        )}
      </div>
    </div>
  );
}
