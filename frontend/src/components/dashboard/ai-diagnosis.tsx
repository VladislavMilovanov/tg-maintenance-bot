"use client";

import { useState, useEffect } from "react";
import { Bot, AlertTriangle, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { createAssistantMessage } from "@/lib/api/endpoints";
import { useAuth } from "@/lib/auth/context";
import { statusConfig } from "@/lib/status-colors";
import type { EquipmentStatusType } from "@/lib/status-colors";

interface AiDiagnosisProps {
  equipmentId: string;
  sensorGroupId: string;
  status: string;
}

interface StructuredDiagnosis {
  cause: string | null;
  actions: string[];
  urgency: string | null;
  rawText: string;
}

function parseDiagnosis(text: string): StructuredDiagnosis {
  const causeMatch = text.match(
    /(?:Вероятная причина|Причина)[:\s]*([\s\S]+?)(?=\n(?:Рекоменд|Срочность|Приоритет|$))/i
  );
  const actionsMatch = text.match(
    /(?:Рекомендуемые действия|Рекомендации)[:\s]*([\s\S]+?)(?=\n(?:Срочность|Приоритет|$))/i
  );
  const urgencyMatch = text.match(/(?:Срочность|Приоритет)[:\s]*([\s\S]+?)$/i);

  const cause = causeMatch?.[1]?.trim() || null;
  const urgency = urgencyMatch?.[1]?.trim() || null;

  let actions: string[] = [];
  if (actionsMatch?.[1]) {
    actions = actionsMatch[1]
      .split(/\n/)
      .map((line) => line.replace(/^\s*[-\d.)\s]+/, "").trim())
      .filter(Boolean);
  }

  return { cause, actions, urgency, rawText: text };
}

function UrgencyBadge({ urgency }: { urgency: string }) {
  const lower = urgency.toLowerCase();
  const isHigh = /немедленно|срочно|высокая|критическ/.test(lower);
  const isMedium = /средняя|в течение/.test(lower);

  if (isHigh) {
    return (
      <Badge className="gap-1 bg-red-100 text-red-700 border-red-300 hover:bg-red-100 dark:bg-red-950/40 dark:text-red-400 dark:border-red-800">
        <Clock className="h-3 w-3" />
        {urgency}
      </Badge>
    );
  }
  if (isMedium) {
    return (
      <Badge className="gap-1 bg-yellow-100 text-yellow-700 border-yellow-300 hover:bg-yellow-100 dark:bg-yellow-950/40 dark:text-yellow-400 dark:border-yellow-800">
        <Clock className="h-3 w-3" />
        {urgency}
      </Badge>
    );
  }
  return (
    <Badge className="gap-1 bg-green-100 text-green-700 border-green-300 hover:bg-green-100 dark:bg-green-950/40 dark:text-green-400 dark:border-green-800">
      <Clock className="h-3 w-3" />
      {urgency}
    </Badge>
  );
}

function StructuredView({ diagnosis }: { diagnosis: StructuredDiagnosis }) {
  const hasStructure = !!diagnosis.cause || diagnosis.actions.length > 0;

  if (!hasStructure) {
    return (
      <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
        {diagnosis.rawText}
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {diagnosis.cause && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
            Вероятная причина
          </p>
          <p className="text-sm text-foreground leading-relaxed">{diagnosis.cause}</p>
        </div>
      )}

      {diagnosis.actions.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
            Рекомендуемые действия
          </p>
          <ol className="space-y-1.5">
            {diagnosis.actions.map((action, i) => (
              <li key={i} className="flex gap-2.5 text-sm text-foreground leading-relaxed">
                <span className="flex-shrink-0 flex items-center justify-center h-5 w-5 rounded-full bg-primary/10 text-primary text-xs font-bold mt-0.5">
                  {i + 1}
                </span>
                <span>{action}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {diagnosis.urgency && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
            Срочность
          </p>
          <UrgencyBadge urgency={diagnosis.urgency} />
        </div>
      )}
    </div>
  );
}

export function AiDiagnosis({ equipmentId, sensorGroupId, status }: AiDiagnosisProps) {
  const { user } = useAuth();
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isCritical = status === "critical";
  const isWarning = status === "warning";
  const isAlert = isCritical || isWarning;

  const statusKey = (isCritical ? "critical" : isWarning ? "warning" : "normal") as EquipmentStatusType;
  const leftBorderClass = isAlert ? `border-l-4 ${statusConfig[statusKey].borderColor}` : "";

  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    createAssistantMessage({
      channel: "web",
      user: {
        external_id: user.external_id,
        display_name: user.display_name ?? undefined,
        role: user.role ?? undefined,
      },
      message: {
        text: "Дай диагностику текущего состояния узла. Опиши что происходит и какие рекомендации.",
      },
      equipment_context: {
        equipment_id: equipmentId,
        sensor_group_ids: [sensorGroupId],
      },
    })
      .then((res) => {
        if (!cancelled) setAnswer(res.answer);
      })
      .catch((err: unknown) => {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Ошибка AI-диагностики");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [user, equipmentId, sensorGroupId]);

  return (
    <Card className={leftBorderClass}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-primary" />
          AI Диагностика
          {isAlert && (
            <AlertTriangle
              className={`h-4 w-4 ${isCritical ? "text-red-500" : "text-yellow-500"}`}
            />
          )}
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
          <div>
            {isAlert && (
              <div
                role="alert"
                className={`mb-4 flex items-start gap-2 rounded-lg border px-4 py-3 text-sm ${
                  isCritical
                    ? "border-red-400/50 bg-red-50 text-red-700 dark:bg-red-950/30 dark:text-red-400"
                    : "border-yellow-400/50 bg-yellow-50 text-yellow-700 dark:bg-yellow-950/30 dark:text-yellow-400"
                }`}
              >
                <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" />
                <span>
                  {isCritical
                    ? "Критическое состояние! Требуется немедленное вмешательство."
                    : "Внимание! Состояние узла требует контроля."}
                </span>
              </div>
            )}
            {answer && <StructuredView diagnosis={parseDiagnosis(answer)} />}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
