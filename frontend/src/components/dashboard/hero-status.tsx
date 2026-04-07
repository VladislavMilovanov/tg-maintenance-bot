"use client";

import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import type { EquipmentStatus, StatusSummary, TrendInfo } from "@/lib/api/types";

interface HeroStatusProps {
  status: EquipmentStatus;
  summary: StatusSummary;
  trend?: TrendInfo | null;
}

function heroBackground(status: EquipmentStatus): string {
  switch (status) {
    case "critical":
      return "bg-red-50 dark:bg-red-950/40 ring-red-200 dark:ring-red-800";
    case "warning":
      return "bg-yellow-50 dark:bg-yellow-950/40 ring-yellow-200 dark:ring-yellow-800";
    case "normal":
      return "bg-green-50 dark:bg-green-950/40 ring-green-200 dark:ring-green-800";
    default:
      return "bg-gray-50 dark:bg-gray-900/40 ring-gray-200 dark:ring-gray-700";
  }
}

function heroHeadingColor(status: EquipmentStatus): string {
  switch (status) {
    case "critical":
      return "text-red-700 dark:text-red-300";
    case "warning":
      return "text-yellow-700 dark:text-yellow-300";
    case "normal":
      return "text-green-700 dark:text-green-300";
    default:
      return "text-gray-700 dark:text-gray-300";
  }
}

function TrendSection({ trend }: { trend?: TrendInfo | null }) {
  if (!trend) return null;
  const totalDelta = trend.critical_delta + trend.warning_delta;

  if (trend.direction === "improved") {
    return (
      <div className="flex items-center gap-1.5 text-green-600 dark:text-green-400 text-sm font-medium">
        <TrendingDown className="h-4 w-4 shrink-0" />
        <span>↓ {Math.abs(totalDelta)} проблем меньше за неделю</span>
      </div>
    );
  }

  if (trend.direction === "worsened") {
    return (
      <div className="flex items-center gap-1.5 text-red-600 dark:text-red-400 text-sm font-medium">
        <TrendingUp className="h-4 w-4 shrink-0" />
        <span>↑ +{totalDelta} за неделю</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1.5 text-muted-foreground text-sm">
      <Minus className="h-4 w-4 shrink-0" />
      <span>Без изменений за неделю</span>
    </div>
  );
}

export function HeroStatus({ status, summary, trend }: HeroStatusProps) {
  const problemCount = summary.warning + summary.critical;
  const isNormal = status === "normal";

  const headingText = isNormal
    ? "Площадка: Всё в норме"
    : `Площадка: ${problemCount} ${problemCount === 1 ? "проблема требует" : problemCount >= 2 && problemCount <= 4 ? "проблемы требуют" : "проблем требуют"} внимания`;

  const bgClass = heroBackground(status);
  const headingColor = heroHeadingColor(status);

  return (
    <Card className={bgClass}>
      <CardContent className="py-5">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex flex-col gap-1">
            <h2 className={`text-xl font-semibold leading-tight ${headingColor}`}>
              {headingText}
            </h2>
            <p className="text-sm text-muted-foreground">
              {summary.normal} в норме
              {" · "}
              {summary.warning} {summary.warning === 1 ? "предупреждение" : "предупреждения"}
              {" · "}
              {summary.critical} {summary.critical === 1 ? "критично" : "критичных"}
              {" · "}
              {summary.unknown} неизвестно
            </p>
          </div>
          {trend && (
            <div className="shrink-0">
              <TrendSection trend={trend} />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
