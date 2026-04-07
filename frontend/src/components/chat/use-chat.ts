"use client";

import { useState, useCallback } from "react";
import { createAssistantMessage } from "@/lib/api/endpoints";
import type { EquipmentContext } from "@/lib/api/types";
import type { AuthMeResponse } from "@/lib/api/types";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  isError?: boolean;
}

interface UseChatOptions {
  user: AuthMeResponse | null;
  equipmentContext?: EquipmentContext | null;
}

interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (text: string) => Promise<void>;
  retryLast: () => Promise<void>;
  conversationId: string | null;
}

export function useChat({ user, equipmentContext }: UseChatOptions): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [lastUserText, setLastUserText] = useState<string | null>(null);

  const doSend = useCallback(
    async (text: string, cancelled: { value: boolean }) => {
      if (!user) {
        setError("Необходима авторизация");
        return;
      }

      setError(null);
      setIsLoading(true);

      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        text,
      };

      setMessages((prev) => [...prev, userMsg]);

      try {
        const response = await createAssistantMessage({
          channel: "web",
          user: {
            external_id: user.external_id,
            display_name: user.display_name ?? undefined,
            role: user.role ?? undefined,
          },
          message: { text },
          conversation_id: conversationId ?? undefined,
          equipment_context: equipmentContext ?? undefined,
        });

        if (cancelled.value) return;

        setConversationId(response.conversation_id);

        const assistantMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          text: response.answer,
        };

        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err) {
        if (cancelled.value) return;

        const errorText =
          err instanceof Error ? err.message : "Произошла ошибка";
        setError(errorText);

        // Remove the user message that failed so retry can re-add it
        setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
      } finally {
        if (!cancelled.value) {
          setIsLoading(false);
        }
      }
    },
    [user, conversationId, equipmentContext],
  );

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isLoading) return;
      setLastUserText(trimmed);
      const cancelled = { value: false };
      await doSend(trimmed, cancelled);
    },
    [isLoading, doSend],
  );

  const retryLast = useCallback(async () => {
    if (!lastUserText || isLoading) return;
    const cancelled = { value: false };
    await doSend(lastUserText, cancelled);
  }, [lastUserText, isLoading, doSend]);

  return { messages, isLoading, error, sendMessage, retryLast, conversationId };
}
