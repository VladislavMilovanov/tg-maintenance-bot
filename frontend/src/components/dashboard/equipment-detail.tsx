"use client";

import { useState, useEffect } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { getEquipmentDetail } from "@/lib/api/endpoints";
import type { EquipmentDetailResponse } from "@/lib/api/types";
import { EquipmentHeader } from "./equipment-header";
import { MaintenanceProgress } from "./maintenance-progress";
import { TopNodes } from "./top-nodes";
import { EquipmentHistory } from "./equipment-history";
import { EquipmentAiSummary } from "./equipment-ai-summary";

interface EquipmentDetailProps {
  equipmentId: string;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function EquipmentDetail({ equipmentId }: EquipmentDetailProps) {
  const [equipment, setEquipment] = useState<EquipmentDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getEquipmentDetail(equipmentId)
      .then((data) => {
        if (!cancelled) {
          setEquipment(data);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Ошибка загрузки оборудования");
          setLoading(false);
        }
      });
    return () => { cancelled = true; };
  }, [equipmentId]);

  if (loading) {
    return (
      <div className="space-y-8">
        <Skeleton className="h-16 w-full rounded-xl" />
        <Skeleton className="h-48 w-full rounded-xl" />
        <Skeleton className="h-28 w-full rounded-xl" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <Skeleton className="h-16 w-full rounded-xl" />
          <Skeleton className="h-16 w-full rounded-xl" />
          <Skeleton className="h-16 w-full rounded-xl" />
          <Skeleton className="h-16 w-full rounded-xl" />
        </div>
        <Skeleton className="h-64 w-full rounded-xl" />
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

  if (!equipment) return null;

  return (
    <div className="space-y-8">
      {/* Header */}
      <EquipmentHeader equipment={equipment} />

      {/* AI Summary - only for warning/critical */}
      {(equipment.current_status === "warning" || equipment.current_status === "critical") && (
        <EquipmentAiSummary equipmentId={equipmentId} status={equipment.current_status} />
      )}

      {/* Nodes — always visible, shown first */}
      <TopNodes nodes={equipment.top_nodes} equipmentId={equipmentId} />

      {/* Maintenance progress */}
      <MaintenanceProgress
        progress={equipment.maintenance_progress}
        dueAt={null}
        completedAt={null}
      />

      {/* Compact metadata grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border border-border bg-card px-4 py-3">
          <p className="text-xs text-muted-foreground">Ответственный</p>
          <p className="text-sm font-medium">{equipment.owner?.display_name ?? "—"}</p>
        </div>
        <div className="rounded-xl border border-border bg-card px-4 py-3">
          <p className="text-xs text-muted-foreground">Групп датчиков</p>
          <p className="text-sm font-medium">{equipment.sensor_groups_count}</p>
        </div>
        <div className="rounded-xl border border-border bg-card px-4 py-3">
          <p className="text-xs text-muted-foreground">Код оборудования</p>
          <p className="text-sm font-medium font-mono">{equipment.equipment_code ?? "—"}</p>
        </div>
        <div className="rounded-xl border border-border bg-card px-4 py-3">
          <p className="text-xs text-muted-foreground">Последнее изменение</p>
          <p className="text-sm font-medium">{formatDate(equipment.last_state_change)}</p>
        </div>
      </div>

      {/* History */}
      <EquipmentHistory equipmentId={equipmentId} />
    </div>
  );
}
