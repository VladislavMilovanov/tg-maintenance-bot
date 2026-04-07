"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/context";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!username.trim()) return;
    setError(null);
    setIsSubmitting(true);
    try {
      await login(username.trim());
      router.push("/dashboard");
    } catch {
      setError("Не удалось войти. Проверьте имя пользователя.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="w-full max-w-sm">
      <div className="rounded-lg border border-border bg-card shadow-sm p-8 space-y-6">
        {/* Brand */}
        <div className="space-y-1 text-center">
          <div className="inline-flex items-center justify-center w-10 h-10 rounded-md bg-primary text-primary-foreground mb-3">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          </div>
          <h1 className="text-xl font-semibold text-foreground">
            Вход в систему мониторинга
          </h1>
          <p className="text-sm text-muted-foreground">
            Введите ваш Telegram username для доступа
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label
              htmlFor="username"
              className="text-sm font-medium text-foreground"
            >
              Telegram Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Введите Telegram username"
              autoComplete="username"
              disabled={isSubmitting}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            />
          </div>

          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}

          <Button
            type="submit"
            className="w-full"
            disabled={isSubmitting || !username.trim()}
          >
            {isSubmitting ? "Вход..." : "Войти"}
          </Button>
        </form>
      </div>
    </div>
  );
}
