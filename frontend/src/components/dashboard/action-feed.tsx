"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { ChevronDown, ChevronRight } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { getActionFeed } from "@/lib/api/endpoints";
import { statusConfig } from "@/lib/status-colors";
import type { EquipmentStatusType } from "@/lib/status-colors";
import type { ActionFeedEntry } from "@/lib/api/types";

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

function ChannelBadge({ channel }: { channel: string }) {
  const labels: Record<string, string> = {
    web: "Веб",
    telegram: "Telegram",
  };
  return (
    <span className="inline-flex items-center rounded-full bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground">
      {labels[channel] ?? channel}
    </span>
  );
}

export function ActionFeed() {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<ActionFeedEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);

  // Lazy-load when expanded for the first time
  useEffect(() => {
    if (!open || loaded) return;
    let cancelled = false;
    setLoading(true);
    getActionFeed({ limit: PAGE_SIZE, offset: 0 })
      .then((res) => {
        if (!cancelled) {
          setItems(res.items);
          setTotal(res.total);
          setLoaded(true);
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
  }, [open, loaded]);

  const loadMore = useCallback(async () => {
    setLoadingMore(true);
    try {
      const res = await getActionFeed({ limit: PAGE_SIZE, offset: items.length });
      setItems((prev) => [...prev, ...res.items]);
      setTotal(res.total);
    } catch {
      // silently fail
    } finally {
      setLoadingMore(false);
    }
  }, [items.length]);

  return (
    <Card>
      <CardHeader
        className="cursor-pointer select-none"
        onClick={() => setOpen((v) => !v)}
      >
        <div className="flex items-center justify-between">
          <span className="font-heading text-base font-medium">Журнал действий</span>
          {open ? (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
      </CardHeader>

      {open && (
        <CardContent className="p-0">
        {loading ? (
          <div className="px-6 py-3 space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-14 w-full rounded-lg" />
            ))}
          </div>
        ) : error ? (
          <p className="px-6 py-4 text-sm text-destructive">{error}</p>
        ) : items.length === 0 ? (
          <p className="px-6 py-4 text-sm text-muted-foreground">Нет действий</p>
        ) : (
          <>
            <div className="divide-y divide-border">
              {items.map((item) => {
                const key = item.status as EquipmentStatusType;
                const config = statusConfig[key] ?? statusConfig.unknown;
                return (
                  <div key={item.record_id} className="px-6 py-3">
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <Link
                        href={`/dashboard/equipment/${item.equipment_id}`}
                        className="text-sm font-medium text-foreground hover:underline"
                      >
                        {item.equipment_name}
                      </Link>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <ChannelBadge channel={item.channel} />
                        <span className="text-xs text-muted-foreground">{formatDate(item.observed_at)}</span>
                      </div>
                    </div>
                    <div className="mt-1 flex items-center gap-2 flex-wrap">
                      <span
                        className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${config.bgColor} ${config.color}`}
                      >
                        <span className={`h-1.5 w-1.5 rounded-full ${config.dotColor}`} />
                        {config.label}
                      </span>
                      {item.author_name && (
                        <span className="text-xs text-muted-foreground">{item.author_name}</span>
                      )}
                    </div>
                    {item.comment && (
                      <p className="mt-1 text-xs text-muted-foreground line-clamp-2">{item.comment}</p>
                    )}
                  </div>
                );
              })}
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
      )}
    </Card>
  );
}
