"use client";

import { useState, useEffect } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { getPlantOverview } from "@/lib/api/endpoints";
import type { PlantOverviewResponse } from "@/lib/api/types";
import { HeroStatus } from "./hero-status";
import { AttentionRequired } from "./attention-required";
import { DailyStatusChart } from "./daily-status-chart";
import { StateFeed } from "./state-feed";
import { ActionFeed } from "./action-feed";

export function PlantDashboard() {
  const [overview, setOverview] = useState<PlantOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getPlantOverview()
      .then((data) => {
        if (!cancelled) setOverview(data);
      })
      .catch((err: unknown) => {
        if (!cancelled)
          setError(
            err instanceof Error ? err.message : "Ошибка загрузки данных дашборда",
          );
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <div className="space-y-8">
        {/* Hero skeleton */}
        <Skeleton className="h-24 w-full rounded-xl" />
        {/* Attention cards skeleton */}
        <Skeleton className="h-48 w-full rounded-xl" />
        {/* Chart skeleton */}
        <Skeleton className="h-80 w-full rounded-xl" />
        {/* Feed skeleton */}
        <Skeleton className="h-56 w-full rounded-xl" />
        {/* Action feed skeleton */}
        <Skeleton className="h-14 w-full rounded-xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-destructive/30 bg-destructive/5 px-6 py-8 text-center">
        <p className="text-sm font-medium text-destructive">{error}</p>
        <p className="mt-1 text-xs text-muted-foreground">
          Проверьте соединение с сервером и попробуйте обновить страницу.
        </p>
      </div>
    );
  }

  if (!overview) return null;

  return (
    <div className="space-y-8">
      {/* 1. Hero — instant situational awareness */}
      <HeroStatus
        status={overview.plant_status}
        summary={overview.status_summary}
        trend={overview.trend}
      />

      {/* 2. Attention required — actionable items */}
      <AttentionRequired items={overview.worst_performers} />

      {/* 3. Daily status chart */}
      <DailyStatusChart data={overview.daily_history} />

      {/* 4. State feed — compact, full width */}
      <StateFeed />

      {/* 5. Action feed — collapsible */}
      <ActionFeed />
    </div>
  );
}
