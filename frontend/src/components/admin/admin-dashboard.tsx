"use client";

import { useState, useEffect } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { getAdminDashboard } from "@/lib/api/endpoints";
import type { AdminDashboardResponse } from "@/lib/api/types";
import { KpiCards } from "./kpi-cards";
import { ActivityChart } from "./activity-chart";
import { ProgressMatrix } from "./progress-matrix";
import { ClientsTable } from "./clients-table";
import { EventsFeed } from "./events-feed";

export function AdminDashboard() {
  const [dashboard, setDashboard] = useState<AdminDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getAdminDashboard()
      .then((data) => {
        if (!cancelled) setDashboard(data);
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
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        {/* KPI skeletons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 w-full rounded-xl" />
          ))}
        </div>
        {/* Chart + Matrix skeletons */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Skeleton className="h-72 w-full rounded-xl" />
          <Skeleton className="h-72 w-full rounded-xl" />
        </div>
        {/* Table + Feed skeletons */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Skeleton className="h-80 w-full rounded-xl" />
          <Skeleton className="h-80 w-full rounded-xl" />
        </div>
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

  if (!dashboard) return null;

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <KpiCards kpis={dashboard.kpis} />

      {/* Chart + Progress Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ActivityChart data={dashboard.activity_chart} />
        <ProgressMatrix data={dashboard.progress_matrix} />
      </div>

      {/* Clients + Events */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ClientsTable />
        <EventsFeed />
      </div>
    </div>
  );
}
