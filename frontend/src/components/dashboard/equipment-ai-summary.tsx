"use client";

import { useState, useEffect, useCallback } from "react";
import { Bot, CheckCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { createAssistantMessage } from "@/lib/api/endpoints";
import { useAuth } from "@/lib/auth/context";
import { statusConfig } from "@/lib/status-colors";
import type { EquipmentStatusType } from "@/lib/status-colors";

interface EquipmentAiSummaryProps {
  equipmentId: string;
  status: string;
}

export function EquipmentAiSummary({ equipmentId, status }: EquipmentAiSummaryProps) {
  const { user } = useAuth();
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isCritical = status === "critical";
  const isWarning = status === "warning";
  const isAlert = isCritical || isWarning;

  const fetchSummary = useCallback(async (signal: AbortSignal) => {
    if (!user) return;
    try {
      const res = await createAssistantMessage({
        channel: "web",
        user: {
          external_id: user.external_id,
          display_name: user.display_name ?? undefined,
          role: user.role ?? undefined,
        },
        message: {
          text: "Дай краткую сводку по состоянию оборудования. Какие узлы в проблеме и что рекомендуется?",
        },
        equipment_context: {
          equipment_id: equipmentId,
        },
      });
      if (!signal.aborted) {
        setAnswer(res.answer);
        setLoading(false);
      }
    } catch (err: unknown) {
      if (!signal.aborted) {
        setError(err instanceof Error ? err.message : "Ошибка AI-сводки");
        setLoading(false);
      }
    }
  }, [user, equipmentId]);

  useEffect(() => {
    if (!isAlert || !user) return;
    const controller = new AbortController();
    /* eslint-disable react-hooks/set-state-in-effect -- legitimate async data-fetching pattern */
    setAnswer(null);
    setError(null);
    setLoading(true);
    void fetchSummary(controller.signal);
    /* eslint-enable react-hooks/set-state-in-effect */
    return () => {
      controller.abort();
    };
  }, [user, equipmentId, isAlert, fetchSummary]);

  // Normal status: compact green card, no API call
  if (status === "normal") {
    return (
      <div className="flex items-center gap-3 rounded-xl border border-green-400/40 bg-green-50 px-4 py-3 dark:bg-green-950/20">
        <CheckCircle className="h-5 w-5 shrink-0 text-green-500" />
        <p className="text-sm font-medium text-green-700 dark:text-green-400">
          Оборудование работает штатно
        </p>
      </div>
    );
  }

  if (!isAlert) return null;

  const statusKey = (isCritical ? "critical" : isWarning ? "warning" : "unknown") as EquipmentStatusType;
  const accentBorder = `border-l-4 ${statusConfig[statusKey].borderColor}`;

  const alertClasses = isCritical
    ? "border-red-400/50 bg-red-50 text-red-700 dark:bg-red-950/30 dark:text-red-400"
    : "border-yellow-400/50 bg-yellow-50 text-yellow-700 dark:bg-yellow-950/30 dark:text-yellow-400";

  return (
    <Card className={accentBorder}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Bot className="h-5 w-5 text-primary" />
          AI Сводка
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-2">
            <Skeleton className="h-4 w-full rounded" />
            <Skeleton className="h-4 w-5/6 rounded" />
            <Skeleton className="h-4 w-4/6 rounded" />
          </div>
        ) : error ? (
          <p className="text-sm text-destructive">{error}</p>
        ) : (
          <div
            role="alert"
            className={`rounded-lg border px-4 py-3 text-sm leading-relaxed ${alertClasses}`}
          >
            <p className="whitespace-pre-wrap">{answer}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
