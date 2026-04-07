"use client";

import Link from "next/link";
import { CheckCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { statusConfig } from "@/lib/status-colors";
import type { EquipmentStatusType } from "@/lib/status-colors";
import type { WorstPerformerEntry } from "@/lib/api/types";

interface AttentionRequiredProps {
  items: WorstPerformerEntry[];
}

function formatDuration(hours: number | null): string {
  if (hours === null) return "";
  if (hours >= 24) {
    const days = Math.floor(hours / 24);
    return `В этом статусе ${days} дн.`;
  }
  return `В этом статусе ${hours} ч.`;
}

function sortItems(items: WorstPerformerEntry[]): WorstPerformerEntry[] {
  return [...items].sort((a, b) => {
    const order: Record<string, number> = { critical: 0, warning: 1 };
    const aOrder = order[a.current_status] ?? 2;
    const bOrder = order[b.current_status] ?? 2;
    return aOrder - bOrder;
  });
}

export function AttentionRequired({ items }: AttentionRequiredProps) {
  const problemItems = items.filter(
    (i) => i.current_status === "critical" || i.current_status === "warning"
  );
  const sorted = sortItems(problemItems);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Требует внимания</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {sorted.length === 0 ? (
          <div className="flex items-center gap-3 px-4 py-5">
            <CheckCircle className="h-5 w-5 shrink-0 text-green-500" />
            <p className="text-sm font-medium text-green-700 dark:text-green-400">
              Все системы работают штатно
            </p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {sorted.map((item) => {
              const key = item.current_status as EquipmentStatusType;
              const config = statusConfig[key] ?? statusConfig.unknown;
              const borderColor = config.borderColor;
              const duration = formatDuration(item.duration_in_status_hours);

              return (
                <div
                  key={item.equipment_id}
                  className={`flex flex-col gap-1.5 border-l-4 ${borderColor} px-4 py-3`}
                >
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <Link
                      href={`/dashboard/equipment/${item.equipment_id}`}
                      className="text-sm font-semibold text-foreground hover:underline"
                    >
                      {item.name}
                    </Link>
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${config.bgColor} ${config.color}`}
                    >
                      <span className={`h-1.5 w-1.5 rounded-full ${config.dotColor}`} />
                      {config.label}
                    </span>
                  </div>

                  <p className="text-sm text-muted-foreground line-clamp-1">
                    {item.last_comment ?? "Нет комментария"}
                  </p>

                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    {duration && (
                      <span className="text-xs text-muted-foreground">{duration}</span>
                    )}
                    <Link
                      href={`/dashboard/equipment/${item.equipment_id}`}
                      className="ml-auto text-xs font-medium text-primary hover:underline"
                    >
                      Подробнее →
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
