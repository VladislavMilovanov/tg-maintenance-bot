"use client";

import { useState, useRef, type KeyboardEvent } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { VoiceInputButton } from "@/components/chat/voice-input-button";

interface ChatInputProps {
  onSend: (text: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSend, isLoading, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || isLoading || disabled) return;
    onSend(trimmed);
    setValue("");
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-border p-3 flex gap-2">
      <Input
        ref={inputRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Введите сообщение..."
        disabled={isLoading || disabled}
        className="flex-1 text-sm h-9"
        aria-label="Введите сообщение"
      />
      <VoiceInputButton
        onTranscript={(text) => {
          setValue((prev) => (prev ? prev + " " + text : text));
          inputRef.current?.focus();
        }}
        disabled={isLoading || disabled}
      />
      <Button
        size="icon"
        className="h-9 w-9 shrink-0"
        onClick={handleSend}
        disabled={!value.trim() || isLoading || disabled}
        aria-label="Отправить"
      >
        <Send className="h-4 w-4" />
      </Button>
    </div>
  );
}
