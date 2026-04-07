"use client";

import { useEffect, useRef } from "react";
import { Loader2 } from "lucide-react";
import type { ChatMessage } from "./use-chat";

interface ChatMessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

export function ChatMessageList({ messages, isLoading }: ChatMessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center p-4">
        <p className="text-sm text-muted-foreground text-center leading-relaxed">
          Задайте вопрос AI-ассистенту
          <br />
          <span className="text-xs opacity-70">
            Я помогу с информацией об оборудовании
          </span>
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-0">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
        >
          <div
            className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm leading-relaxed ${
              msg.role === "user"
                ? "bg-primary text-primary-foreground rounded-br-sm"
                : "bg-muted text-foreground rounded-bl-sm"
            }`}
          >
            {msg.text}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-muted text-muted-foreground rounded-2xl rounded-bl-sm px-3 py-2 flex items-center gap-1.5">
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            <span className="text-sm">Думаю...</span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
