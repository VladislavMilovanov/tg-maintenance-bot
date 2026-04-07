"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { listAdminEvents } from "@/lib/api/endpoints";
import type { AdminEventEntry, AdminEventsResponse } from "@/lib/api/types";

const PAGE_SIZE = 15;

function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    return d.toLocaleString("ru-RU", {
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

function eventTypeLabel(eventType: string): string {
  const map: Record<string, string> = {
    state_change: "Смена статуса",
    login: "Вход",
    logout: "Выход",
    record_created: "Запись создана",
    comment_added: "Комментарий",
  };
  return map[eventType] ?? eventType;
}

interface EventRowProps {
  event: AdminEventEntry;
}

function EventRow({ event }: EventRowProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-start gap-2 py-3 px-4 border-b border-border last:border-0 hover:bg-muted/30 transition-colors">
      <div className="flex items-center gap-2 sm:w-40 shrink-0">
        <Badge variant="outline" className="text-xs whitespace-nowrap">
          {eventTypeLabel(event.event_type)}
        </Badge>
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          {event.equipment_name && (
            <span className="font-medium text-sm text-foreground truncate">
              {event.equipment_name}
            </span>
          )}
        </div>
        <p className="text-sm text-muted-foreground line-clamp-2 mt-0.5">
          {event.description}
        </p>
        {event.actor_name && (
          <p className="text-xs text-muted-foreground mt-0.5">
            Автор: {event.actor_name}
          </p>
        )}
      </div>

      <div className="text-xs text-muted-foreground whitespace-nowrap sm:text-right shrink-0">
        {formatDate(event.occurred_at)}
      </div>
    </div>
  );
}

export function EventsFeed() {
  const [items, setItems] = useState<AdminEventEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    listAdminEvents({ limit: PAGE_SIZE, offset: 0 })
      .then((res: AdminEventsResponse) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Ошибка загрузки событий");
      })
      .finally(() => setLoading(false));
  }, []);

  const handleLoadMore = async () => {
    setLoadingMore(true);
    try {
      const res = await listAdminEvents({
        limit: PAGE_SIZE,
        offset: items.length,
      });
      setItems((prev) => [...prev, ...res.items]);
      setTotal(res.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки событий");
    } finally {
      setLoadingMore(false);
    }
  };

  const hasMore = items.length < total;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Лента событий</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {loading && (
          <div className="px-4 py-4 space-y-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        )}

        {error && (
          <div className="px-4 py-6 text-sm text-destructive">{error}</div>
        )}

        {!loading && !error && items.length === 0 && (
          <div className="px-4 py-8 text-center text-sm text-muted-foreground">
            Событий пока нет
          </div>
        )}

        {!loading && items.length > 0 && (
          <>
            <div>
              {items.map((event, idx) => (
                <EventRow key={`${event.occurred_at}-${idx}`} event={event} />
              ))}
            </div>
            {hasMore && (
              <div className="flex justify-center p-4 border-t border-border">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLoadMore}
                  disabled={loadingMore}
                >
                  {loadingMore ? "Загрузка..." : "Загрузить ещё"}
                </Button>
              </div>
            )}
            {!hasMore && (
              <div className="px-4 py-3 text-center text-xs text-muted-foreground border-t border-border">
                Показано {items.length} из {total}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
