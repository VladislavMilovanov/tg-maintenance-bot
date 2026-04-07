"use client";

import { useState, useRef } from "react";
import { Mic, Square } from "lucide-react";
import { Button } from "@/components/ui/button";

interface VoiceInputButtonProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

function getSpeechRecognitionConstructor(): (new () => SpeechRecognition) | null {
  if (typeof window === "undefined") return null;
  return window.SpeechRecognition ?? window.webkitSpeechRecognition ?? null;
}

export function VoiceInputButton({
  onTranscript,
  disabled,
}: VoiceInputButtonProps) {
  // Lazy initial state — runs once on mount (client only), safe for SSR
  const [isSupported] = useState<boolean>(
    () => getSpeechRecognitionConstructor() !== null,
  );
  const [isRecording, setIsRecording] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const startRecording = () => {
    const SR = getSpeechRecognitionConstructor();
    if (!SR) return;

    const recognition = new SR();
    recognition.lang = "ru-RU";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      // Silently ignore "no-speech" — user just didn't say anything
      if (event.error !== "no-speech") {
        console.warn("Speech recognition error:", event.error);
      }
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    recognitionRef.current?.stop();
    setIsRecording(false);
  };

  const handleClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  // Not supported — show disabled button with native tooltip
  if (!isSupported) {
    return (
      <Button
        type="button"
        size="icon"
        variant="ghost"
        className="h-9 w-9 shrink-0 opacity-40 cursor-not-allowed"
        disabled
        aria-label="Голосовой ввод недоступен"
        title="Voice input not supported in this browser"
      >
        <Mic className="h-4 w-4" />
      </Button>
    );
  }

  return (
    <Button
      type="button"
      size="icon"
      variant={isRecording ? "destructive" : "ghost"}
      className={[
        "h-9 w-9 shrink-0 transition-all",
        isRecording ? "animate-pulse" : "",
      ]
        .join(" ")
        .trim()}
      onClick={handleClick}
      disabled={disabled}
      aria-label={isRecording ? "Остановить запись" : "Начать голосовой ввод"}
    >
      {isRecording ? (
        <Square className="h-4 w-4" />
      ) : (
        <Mic className="h-4 w-4" />
      )}
    </Button>
  );
}
