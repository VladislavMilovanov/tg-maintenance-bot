"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { getEquipmentHistory } from "@/lib/api/endpoints";
import { statusConfig } from "@/lib/status-colors";
import type { EquipmentStatusType } from "@/lib/status-colors";
import type { EquipmentHistoryEntry } from "@/lib/api/types";

const PAGE_SIZE = 10;

function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return dateStr;
  }
}

const channelLabels: Record<string, string> = {
  web: "Веб",
  telegram: "Telegram",
};

interface EquipmentHistoryProps {
  equipmentId: string;
}

export function EquipmentHistory({ equipmentId }: EquipmentHistoryProps) {
  const [items, setItems] = useState<EquipmentHistoryEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setItems([]);
    getEquipmentHistory(equipmentId, { limit: PAGE_SIZE, offset: 0 })
      .then((res) => {
        if (!cancelled) {
          setItems(res.items);
          setTotal(res.total);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Ошибка загрузки истории");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [equipmentId]);

  const loadMore = useCallback(async () => {
    setLoadingMore(true);
    try {
      const res = await getEquipmentHistory(equipmentId, { limit: PAGE_SIZE, offset: items.length });
      setItems((prev) => [...prev, ...res.items]);
      setTotal(res.total);
    } catch {
      // silently fail
    } finally {
      setLoadingMore(false);
    }
  }, [equipmentId, items.length]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>История состояний</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {loading ? (
          <div className="px-6 py-3 space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full rounded-lg" />
            ))}
          </div>
        ) : error ? (
          <p className="px-6 py-4 text-sm text-destructive">{error}</p>
        ) : items.length === 0 ? (
          <p className="px-6 py-4 text-sm text-muted-foreground">История пуста</p>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">Статус</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">Комментарий</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">Автор</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">Дата</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">Канал</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {items.map((item) => {
                    const key = item.status as EquipmentStatusType;
                    const config = statusConfig[key] ?? statusConfig.unknown;
                    return (
                      <tr key={item.record_id} className="hover:bg-muted/30 transition-colors">
                        <td className="px-6 py-3">
                          <span
                            className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${config.bgColor} ${config.color}`}
                          >
                            <span className={`h-1.5 w-1.5 rounded-full ${config.dotColor}`} />
                            {config.label}
                          </span>
                        </td>
                        <td className="px-6 py-3 max-w-[200px]">
                          <span className="text-muted-foreground line-clamp-2">
                            {item.comment ?? "—"}
                          </span>
                        </td>
                        <td className="px-6 py-3 text-muted-foreground whitespace-nowrap">
                          {item.author?.display_name ?? item.author?.external_id ?? "—"}
                        </td>
                        <td className="px-6 py-3 text-muted-foreground whitespace-nowrap">
                          {formatDate(item.observed_at)}
                        </td>
                        <td className="px-6 py-3 text-muted-foreground whitespace-nowrap">
                          {channelLabels[item.channel] ?? item.channel}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            {items.length < total && (
              <div className="px-6 py-4 border-t border-border">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadMore}
                  disabled={loadingMore}
                  className="w-full"
                >
                  {loadingMore ? "Загрузка..." : "Загрузить ещё"}
                </Button>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
