"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { getStateFeed } from "@/lib/api/endpoints";
import { statusConfig } from "@/lib/status-colors";
import type { EquipmentStatusType } from "@/lib/status-colors";
import type { StateChangeEntry } from "@/lib/api/types";

const PAGE_SIZE = 10;

function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return dateStr;
  }
}

function StatusChip({ status }: { status: string }) {
  const key = status as EquipmentStatusType;
  const config = statusConfig[key] ?? statusConfig.unknown;
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${config.bgColor} ${config.color}`}
    >
      {config.label}
    </span>
  );
}

export function StateFeed() {
  const [items, setItems] = useState<StateChangeEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getStateFeed({ limit: PAGE_SIZE, offset: 0 })
      .then((res) => {
        if (!cancelled) {
          setItems(res.items);
          setTotal(res.total);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Ошибка загрузки");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  const loadMore = useCallback(async () => {
    setLoadingMore(true);
    try {
      const res = await getStateFeed({ limit: PAGE_SIZE, offset: items.length });
      setItems((prev) => [...prev, ...res.items]);
      setTotal(res.total);
    } catch {
      // silently fail for pagination
    } finally {
      setLoadingMore(false);
    }
  }, [items.length]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Лента изменений</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {loading ? (
          <div className="px-6 py-3 space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full rounded-lg" />
            ))}
          </div>
        ) : error ? (
          <p className="px-6 py-4 text-sm text-destructive">{error}</p>
        ) : items.length === 0 ? (
          <p className="px-6 py-4 text-sm text-muted-foreground">Нет изменений</p>
        ) : (
          <>
            <div className="divide-y divide-border">
              {items.map((item) => (
                <div key={`${item.equipment_id}-${item.changed_at}`} className="px-6 py-2">
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <Link
                      href={`/dashboard/equipment/${item.equipment_id}`}
                      className="text-sm font-medium text-foreground hover:underline"
                    >
                      {item.equipment_name}
                    </Link>
                    <span className="text-xs text-muted-foreground">{formatDate(item.changed_at)}</span>
                  </div>
                  <div className="mt-1 flex items-center gap-2 flex-wrap">
                    {item.old_status ? (
                      <StatusChip status={item.old_status} />
                    ) : (
                      <span className="text-xs text-muted-foreground">—</span>
                    )}
                    <span className="text-xs text-muted-foreground">→</span>
                    <StatusChip status={item.new_status} />
                  </div>
                </div>
              ))}
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
